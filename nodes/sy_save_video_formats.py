"""Save Video Formats SY: saves a batch of frames as mp4, webm, gif or animated webp in the output folder."""
import os
import re

try:
    from ._sy_safe_paths import root_folder, safe_join
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_safe_paths import root_folder, safe_join
    from _sy_common import category, register

FORMATS = ("mp4_h264", "webm_vp9", "gif", "webp_animated")
QUALITIES = ("low", "medium", "high")
EXTENSIONS = {"mp4_h264": ".mp4", "webm_vp9": ".webm", "gif": ".gif", "webp_animated": ".webp"}
SUBFOLDER = "sy_video"
COUNTER_WIDTH = 5
_BAD_CHARS = set('<>:"/\\|?*')
_RESERVED = {"con", "prn", "aux", "nul"} | {"com%d" % i for i in range(1, 10)} | {"lpt%d" % i for i in range(1, 10)}
_SETTINGS = {
    "mp4_h264": {"low": {"codec": "libx264", "crf": 28}, "medium": {"codec": "libx264", "crf": 23}, "high": {"codec": "libx264", "crf": 18}},
    "webm_vp9": {"low": {"codec": "libvpx-vp9", "crf": 42}, "medium": {"codec": "libvpx-vp9", "crf": 33}, "high": {"codec": "libvpx-vp9", "crf": 24}},
    "gif": {"low": {"colors": 64}, "medium": {"colors": 128}, "high": {"colors": 256}},
    "webp_animated": {"low": {"quality": 50}, "medium": {"quality": 75}, "high": {"quality": 92}},
}


def safe_prefix(prefix):
    """Pure function. Returns the prefix if it is a plain name. No folders, no '..', no characters Windows refuses."""
    text = str(prefix if prefix is not None else "")
    if not text.strip():
        raise ValueError("filename_prefix is empty: type a short name such as sy_video")
    if text != text.strip() or text.endswith("."):
        raise ValueError("filename_prefix must not start or end with a space, or end with a dot: %r" % text)
    if ".." in text:
        raise ValueError("filename_prefix must not contain '..': %r" % text)
    if "/" in text or "\\" in text:
        raise ValueError("filename_prefix must not contain a slash. The file always goes into the %s folder: %r" % (SUBFOLDER, text))
    bad = sorted(c for c in set(text) if c in _BAD_CHARS or ord(c) < 32)
    if bad:
        raise ValueError("filename_prefix has characters that are not allowed %r. Use letters, digits, - and _" % "".join(bad))
    if len(text) > 100:
        raise ValueError("filename_prefix is too long (%d characters, max 100)" % len(text))
    if text.split(".")[0].lower() in _RESERVED:
        raise ValueError("filename_prefix is a reserved Windows name: %r" % text)
    return text


def next_free_name(existing_names, prefix, ext):
    """Pure function. prefix_00001.ext, numbered after the highest number already used for this prefix and extension."""
    prefix = safe_prefix(prefix)
    ext = str(ext).lower()
    if not re.fullmatch(r"\.[a-z0-9]{1,8}", ext):
        raise ValueError("extension must look like .mp4, got %r" % ext)
    rx = re.compile("^" + re.escape(prefix.lower()) + r"_(\d+)" + re.escape(ext) + "$")
    highest = 0
    for name in existing_names:
        m = rx.match(str(name).lower())
        if m:
            highest = max(highest, int(m.group(1)))
    return "%s_%0*d%s" % (prefix, COUNTER_WIDTH, highest + 1, ext)


def quality_to_settings(format, quality):
    """Pure function. (format, quality) -> dict of encoder settings: crf for mp4/webm, colors for gif, quality for webp."""
    if format not in _SETTINGS:
        raise ValueError("format must be one of %s, got %r" % (", ".join(FORMATS), format))
    if quality not in QUALITIES:
        raise ValueError("quality must be one of %s, got %r" % (", ".join(QUALITIES), quality))
    return dict(_SETTINGS[format][quality])


def even_size(w, h):
    """Pure function. h264 and vp9 (yuv420) need even sizes: crop one pixel when odd."""
    w, h = int(w), int(h)
    if w < 2 or h < 2:
        raise ValueError("pictures must be at least 2x2 pixels, got %dx%d" % (w, h))
    return w - (w % 2), h - (h % 2)


def frame_duration_ms(fps):
    """Pure function. Milliseconds per frame for gif and webp (at least 1)."""
    fps = float(fps)
    if not fps > 0:
        raise ValueError("fps must be above 0, got %r" % fps)
    return max(1, int(round(1000.0 / fps)))


def _frames_to_arrays(images, crop_even):
    import numpy as np
    n, h, w = int(images.shape[0]), int(images.shape[1]), int(images.shape[2])
    if n < 1:
        raise ValueError("no frames to save")
    if crop_even:
        w, h = even_size(w, h)
    for i in range(n):
        arr = images[i, :h, :w, :3].detach().cpu().numpy()
        yield np.clip(arr * 255.0 + 0.5, 0, 255).astype(np.uint8)


def _save_pil(images, path, format, settings, fps):
    from PIL import Image

    pils = (Image.fromarray(a, "RGB") for a in _frames_to_arrays(images, False))
    first = next(pils)
    rest = list(pils)
    dur = frame_duration_ms(fps)
    if format == "gif":
        colors = settings["colors"]
        q = lambda im: im.quantize(colors=colors)
        frames = [q(first)] + [q(p) for p in rest]
        frames[0].save(path, format="GIF", save_all=True, append_images=frames[1:], duration=dur, loop=0, optimize=False)
    else:
        first.save(path, format="WEBP", save_all=True, append_images=rest, duration=dur, loop=0,
                   quality=settings["quality"], method=4)


def _add_audio(container, audio, format, seconds):
    """Adds an audio stream and returns a function that writes the audio. Audio is cut to the video length."""
    import av
    import numpy as np

    wave = audio["waveform"]
    rate = int(audio["sample_rate"])
    data = wave[0].detach().cpu().float().numpy()          # channels x samples
    channels = data.shape[0]
    if channels not in (1, 2):
        data = data[:2] if channels > 2 else data
        channels = data.shape[0]
    data = data[:, : max(1, int(seconds * rate))]
    if format == "webm_vp9":
        codec, out_rate = "libopus", 48000
    else:
        codec, out_rate = "aac", rate
    layout = "mono" if channels == 1 else "stereo"
    stream = container.add_stream(codec, rate=out_rate, layout=layout)
    resampler = av.AudioResampler(format=stream.codec_context.format.name if stream.codec_context.format else "fltp",
                                  layout=layout, rate=out_rate)
    frame_size = stream.codec_context.frame_size or 1024
    fifo = av.AudioFifo()

    def write():
        packed = np.ascontiguousarray(np.clip(data, -1.0, 1.0).T.reshape(1, -1)).astype(np.float32)
        frame = av.AudioFrame.from_ndarray(packed, format="flt", layout=layout)
        frame.sample_rate = rate
        pts = 0
        for out in resampler.resample(frame) + resampler.resample(None):
            fifo.write(out)
        while fifo.samples >= frame_size:
            chunk = fifo.read(frame_size)
            chunk.pts = pts
            pts += chunk.samples
            container.mux(stream.encode(chunk))
        rest = fifo.read(fifo.samples) if fifo.samples else None
        if rest is not None:
            rest.pts = pts
            container.mux(stream.encode(rest))
        container.mux(stream.encode(None))
    return write


def _save_av(images, path, format, settings, fps, audio):
    from fractions import Fraction
    import av

    n = int(images.shape[0])
    w, h = even_size(images.shape[2], images.shape[1])
    container = av.open(path, mode="w")
    try:
        rate = Fraction(float(fps)).limit_denominator(1001)
        stream = container.add_stream(settings["codec"], rate=rate)
        stream.width, stream.height, stream.pix_fmt = w, h, "yuv420p"
        if format == "mp4_h264":
            stream.options = {"crf": str(settings["crf"]), "preset": "medium"}
        else:
            stream.options = {"crf": str(settings["crf"]), "b": "0", "row-mt": "1", "cpu-used": "4"}
        write_audio = _add_audio(container, audio, format, n / float(fps)) if audio is not None else None
        for arr in _frames_to_arrays(images, True):
            frame = av.VideoFrame.from_ndarray(arr, format="rgb24")
            for packet in stream.encode(frame.reformat(format="yuv420p")):
                container.mux(packet)
        for packet in stream.encode(None):
            container.mux(packet)
        if write_audio is not None:
            write_audio()
    finally:
        container.close()


def save_video(images, folder, name, format, quality, fps, audio=None):
    """Writes the frames to folder/name. Needs torch tensors. Returns the full path."""
    settings = quality_to_settings(format, quality)
    path = os.path.join(folder, name)
    if os.path.exists(path):
        raise ValueError("a file with this name already exists: %s. Run it again." % name)
    if format in ("gif", "webp_animated"):
        _save_pil(images, path, format, settings, fps)
    else:
        try:
            import av  # noqa: F401
        except ImportError:
            raise ValueError("saving mp4 or webm needs the 'av' package, which is not installed here. Pick gif or webp_animated instead")
        try:
            _save_av(images, path, format, settings, fps, audio)
        except Exception:
            if os.path.exists(path):
                os.remove(path)
            raise
    return path


class SYSaveVideoFormats:
    DESCRIPTION = ("Saves a batch of frames as an mp4 (h264), webm (vp9), gif or animated webp in the output folder, "
                   "inside a sy_video subfolder. Never overwrites a file. Audio is used for mp4 and webm only.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("path",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames to save, in order."}),
                "fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 120.0, "step": 0.01, "tooltip": "Frames per second of the saved clip."}),
                "format": (list(FORMATS), {"default": "mp4_h264", "tooltip": "File type. mp4 and webm are videos, gif and webp are animated pictures."}),
                "quality": (list(QUALITIES), {"default": "medium", "tooltip": "Higher quality gives a bigger file."}),
                "filename_prefix": ("STRING", {"default": "sy_video", "tooltip": "Start of the file name. No slashes or '..'. A number is added."}),
            },
            "optional": {
                "audio": ("AUDIO", {"tooltip": "Sound for mp4 and webm. It is cut to the length of the video. Ignored for gif and webp."}),
            },
        }

    def run(self, images, fps, format, quality, filename_prefix="sy_video", audio=None):
        prefix = safe_prefix(filename_prefix)
        quality_to_settings(format, quality)
        frame_duration_ms(fps)
        if images.dim() != 4 or images.shape[0] < 1:
            raise ValueError("images must be a batch with at least one frame")
        if audio is not None and not (isinstance(audio, dict) and "waveform" in audio and "sample_rate" in audio):
            raise ValueError("audio must come from a node that gives AUDIO (waveform and sample_rate)")
        out_root = root_folder("output")
        folder = safe_join(out_root, SUBFOLDER)
        os.makedirs(folder, exist_ok=True)
        ext = EXTENSIONS[format]
        name = next_free_name(os.listdir(folder), prefix, ext)
        path = save_video(images, folder, name, format, quality, fps, audio if format in ("mp4_h264", "webm_vp9") else None)
        ui = {"text": [path]}
        if format in ("gif", "webp_animated"):
            ui = {"images": [{"filename": name, "subfolder": SUBFOLDER, "type": "output"}], "animated": (True,)}
        return {"ui": ui, "result": (path,)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SaveVideoFormats", SYSaveVideoFormats)
NODE_DISPLAY_NAME_MAPPINGS["SYSaveVideoFormats"] = "Save Video Formats SY"
