"""Video File Upscale SY: upscales a long video file chunk by chunk, so the whole video is never held in memory."""
import os

try:
    from ._sy_common import category, register, safe_join
    from ._sy_core_call import core, is_out_of_memory
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register, safe_join
    from _sy_core_call import core, is_out_of_memory

OOM_MESSAGE = "Not enough graphics memory even for one frame. Lower longest_side."


def final_size(w, h, longest):
    """Pure function. Final (width, height): the longest side becomes `longest`, the shape stays, both numbers are even."""
    w, h, longest = int(w), int(h), int(longest)
    if w < 1 or h < 1:
        raise ValueError("video size must be at least 1x1, got %dx%d" % (w, h))
    if longest < 2:
        raise ValueError("longest_side must be at least 2, got %d" % longest)
    scale = longest / float(max(w, h))
    fw = max(2, int(round(w * scale / 2.0)) * 2)
    fh = max(2, int(round(h * scale / 2.0)) * 2)
    return fw, fh


def chunk_ranges(count, chunk):
    """Pure function. Splits `count` frames into (start, end) pieces of at most `chunk` frames."""
    count, chunk = int(count), int(chunk)
    if count < 1:
        raise ValueError("the video has no frames")
    if chunk < 1:
        raise ValueError("chunk_frames must be at least 1, got %d" % chunk)
    return [(s, min(count, s + chunk)) for s in range(0, count, chunk)]


def blend_weights(strength):
    """Pure function. (weight of the model result, weight of the plain enlargement). They add up to 1."""
    s = float(strength)
    if not 0.0 <= s <= 1.0:  # also rejects nan
        raise ValueError("detail_strength must be between 0 and 1, got %s" % s)
    return s, 1.0 - s


def blend_values(model_vals, plain_vals, strength):
    """Pure function on plain lists: s * model + (1 - s) * plain."""
    wm, wp = blend_weights(strength)
    if len(model_vals) != len(plain_vals):
        raise ValueError("both lists need the same length")
    return [wm * a + wp * b for a, b in zip(model_vals, plain_vals)]


def output_name(prefix, counter):
    """Pure function. 'SY/upscaled' and 5 -> 'SY/upscaled_00005.mp4'. The prefix may hold a sub folder, never '..'."""
    raw = str(prefix or "").strip().replace("\\", "/")
    if raw.startswith("/"):
        raise ValueError("filename_prefix must stay inside the output folder: no '..', no drive letters.")
    text = raw.strip("/")
    if not text:
        raise ValueError("filename_prefix is empty. Write a name such as SY/upscaled.")
    if os.path.isabs(text) or ":" in text or any(p == ".." for p in text.split("/")):
        raise ValueError("filename_prefix must stay inside the output folder: no '..', no drive letters.")
    if int(counter) < 0:
        raise ValueError("counter must be 0 or more")
    return "%s_%05d.mp4" % (text, int(counter))


def check_video_name(name):
    """Pure function. Returns the cleaned name or raises ValueError for empty, absolute or '..' names."""
    text = str(name or "").strip().strip('"')
    if not text:
        raise ValueError("video is empty. Write the file name of a video in the ComfyUI input folder.")
    norm = text.replace("\\", "/")
    if norm.startswith("/") or (len(norm) > 1 and norm[1] == ":") or os.path.isabs(text):
        raise ValueError("video must be a name inside the ComfyUI input folder, not a full path: %s" % text)
    if any(p == ".." for p in norm.split("/")):
        raise ValueError("video may not contain '..': %s" % text)
    return norm


def info_text(src, final, frames, chunks, strength, sound):
    """Pure function. One line telling what happened."""
    return "%dx%d -> %dx%d, %d frames in %d chunks, detail %g, %s" % (
        src[0], src[1], final[0], final[1], frames, chunks, strength,
        "sound copied" if sound else "no sound in the source")


def find_video(name):
    """Looks for the cleaned name in ComfyUI's input, output and temp folders. Returns the full path."""
    import folder_paths
    clean = check_video_name(name)
    roots = [folder_paths.get_input_directory(), folder_paths.get_output_directory(), folder_paths.get_temp_directory()]
    for root in roots:
        path = safe_join(root, clean)
        if os.path.isfile(path):
            return path
    raise ValueError("no video named %r in the ComfyUI input, output or temp folder. Put the file in the input folder." % clean)


def next_output_path(prefix):
    """First free output path for the prefix, inside ComfyUI's output folder."""
    import folder_paths
    out_root = folder_paths.get_output_directory()
    counter = 1
    while True:
        path = safe_join(out_root, output_name(prefix, counter))
        if not os.path.exists(path):
            break
        counter += 1
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def _resize(batch, width, height):
    """batch: float tensor (N, H, W, 3), values 0..1. Smooth resize to (width, height)."""
    import torch
    if (batch.shape[2], batch.shape[1]) == (width, height):
        return batch
    x = batch.permute(0, 3, 1, 2)
    x = torch.nn.functional.interpolate(x, size=(height, width), mode="bicubic", align_corners=False,
                                        antialias=(width < batch.shape[2] or height < batch.shape[1]))
    return x.permute(0, 2, 3, 1).clamp(0.0, 1.0)


def _model_safe(upscale_fn, batch):
    """Runs the model; on a memory error splits the batch in halves. One frame that still fails raises ValueError."""
    try:
        return upscale_fn(batch)
    except Exception as e:
        if not is_out_of_memory(e):
            raise
        if batch.shape[0] <= 1:
            raise ValueError(OOM_MESSAGE)
    import torch
    half = batch.shape[0] // 2
    left = _model_safe(upscale_fn, batch[:half])
    right = _model_safe(upscale_fn, batch[half:])
    return torch.cat([left, right], dim=0)


def process_chunk(frames_u8, upscale_fn, final, strength):
    """frames_u8: list of (H, W, 3) uint8 numpy arrays. Returns a (N, fh, fw, 3) uint8 numpy array."""
    import numpy as np
    import torch
    batch = torch.from_numpy(np.stack(frames_u8)).float().div_(255.0)
    wm, wp = blend_weights(strength)
    result = None
    if wm > 0.0:
        model_out = _resize(_model_safe(upscale_fn, batch).detach().cpu().float(), final[0], final[1])
        result = model_out if wm == 1.0 else model_out * wm
    if wp > 0.0:
        plain = _resize(batch, final[0], final[1])
        result = plain if result is None else result + plain * wp
    out = (result.clamp(0.0, 1.0) * 255.0 + 0.5).to(torch.uint8).numpy()
    del batch, result
    return out


def upscale_file(src_path, dst_path, upscale_fn, longest, strength, chunk_frames):
    """Reads src_path chunk by chunk, upscales, writes dst_path (H.264, same fps), copies sound. Returns the info text."""
    import av
    from fractions import Fraction
    blend_weights(strength)
    if int(chunk_frames) < 1:
        raise ValueError("chunk_frames must be at least 1, got %s" % chunk_frames)
    inp = av.open(src_path)
    out = None
    try:
        vin = next((s for s in inp.streams if s.type == "video"), None)
        if vin is None:
            raise ValueError("this file has no picture track: %s" % os.path.basename(src_path))
        ain = next((s for s in inp.streams if s.type == "audio"), None)
        src = (int(vin.codec_context.width), int(vin.codec_context.height))
        final = final_size(src[0], src[1], longest)
        rate = vin.average_rate or vin.guessed_rate or Fraction(25, 1)
        out = av.open(dst_path, "w")
        vout = out.add_stream("libx264", rate=rate)
        vout.width, vout.height, vout.pix_fmt = final[0], final[1], "yuv420p"
        vout.options = {"crf": "18"}
        aout = None
        if ain is not None:
            try:
                aout = out.add_stream_from_template(ain)
            except AttributeError:
                aout = out.add_stream(template=ain)
        state = {"frames": 0, "chunks": 0, "pending": []}

        def flush():
            if not state["pending"]:
                return
            pixels = process_chunk(state["pending"], upscale_fn, final, strength)
            state["pending"] = []
            for i in range(pixels.shape[0]):
                frame = av.VideoFrame.from_ndarray(pixels[i], format="rgb24")
                frame.pts = state["frames"]
                frame.time_base = 1 / Fraction(rate)
                state["frames"] += 1
                for pkt in vout.encode(frame.reformat(format="yuv420p")):
                    out.mux(pkt)
            state["chunks"] += 1
            del pixels

        streams = [vin] + ([ain] if ain is not None else [])
        for pkt in inp.demux(*streams):
            if pkt.stream.type == "video":
                for frame in pkt.decode():
                    state["pending"].append(frame.to_ndarray(format="rgb24"))
                    if len(state["pending"]) >= int(chunk_frames):
                        flush()
            elif aout is not None and pkt.dts is not None:
                pkt.stream = aout
                out.mux(pkt)
        flush()
        for pkt in vout.encode():
            out.mux(pkt)
        if state["frames"] < 1:
            raise ValueError("no frames could be read from %s" % os.path.basename(src_path))
        return info_text(src, final, state["frames"], state["chunks"], float(strength), aout is not None)
    finally:
        if out is not None:
            out.close()
        inp.close()


class SYVideoFileUpscale:
    DESCRIPTION = ("Upscales a long video file without running out of memory. It reads a few frames at a time, enlarges them "
                   "with the upscale model, writes them to a new video and copies the sound unchanged.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("video_path", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "video": ("STRING", {"default": "", "tooltip": "File name of a video in the ComfyUI input folder."}),
            "upscale_model": ("UPSCALE_MODEL", {"tooltip": "The model from the Load Upscale Model node."}),
            "longest_side": ("INT", {"default": 1920, "min": 256, "max": 8192, "step": 16, "tooltip": "Final size of the longest side in pixels. The shape stays."}),
            "detail_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "1 = model result. Lower blends in a smooth enlargement to calm sharp skin."}),
            "chunk_frames": ("INT", {"default": 16, "min": 1, "max": 256, "tooltip": "Frames handled at once. Lower uses less memory."}),
            "filename_prefix": ("STRING", {"default": "SY/upscaled", "tooltip": "Name for the new video in the output folder. A sub folder is allowed."}),
        }}

    def run(self, video, upscale_model, longest_side, detail_strength, chunk_frames, filename_prefix):
        src = find_video(video)
        dst = next_output_path(filename_prefix)

        def model_fn(batch):
            return core("ImageUpscaleWithModel", "Video File Upscale SY", upscale_model=upscale_model, image=batch)[0]

        try:
            info = upscale_file(src, dst, model_fn, longest_side, detail_strength, chunk_frames)
        except BaseException:
            try:
                if os.path.isfile(dst):
                    os.remove(dst)  # our own half-written file, never the source
            except OSError:
                pass
            raise
        return (dst, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoFileUpscale", SYVideoFileUpscale)
