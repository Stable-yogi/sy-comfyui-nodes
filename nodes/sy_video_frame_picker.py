"""Video Frame Picker SY: shows a video inside the node with a timeline slider. Scrub to the frame you want and leave the
slider there; when the workflow runs, that exact frame comes out as a picture (plus its frame number and time).
The slider panel lives in js/sy_video_frame_picker.js and writes the frame number into the "frame" widget, so the saved
workflow keeps the chosen frame. Decoding uses PyAV, which ComfyUI already ships with."""
import os

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

NONE = "(none)"
VIDEO_EXT = (".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v", ".gif")
MAX_FRAME = 10_000_000


def pick_videos(names):
    """Pure function. The video file names, sorted, with (none) first."""
    return [NONE] + sorted(n for n in names if os.path.splitext(n)[1].lower() in VIDEO_EXT)


def clamp_frame(frame, total):
    """Pure function. (frame index to use, note). total 0 = unknown length: the frame is kept as asked."""
    frame = int(frame)
    if frame < 0:
        raise ValueError("the frame number cannot be negative")
    total = int(total or 0)
    if total > 0 and frame >= total:
        return total - 1, "frame %d is past the end; the last frame (%d) was used" % (frame, total - 1)
    return frame, ""


def frame_of_time(seconds, fps):
    """Pure function. Frame number that shows at a time in seconds (frame i covers i/fps up to (i+1)/fps)."""
    fps = float(fps)
    if fps <= 0:
        raise ValueError("the video has no frame rate")
    return max(0, int(round(float(seconds) * fps + 1e-6)))


def info_text(name, index, total, fps, width, height, note=""):
    """Pure function. One readable block about the picked frame."""
    seconds = index / float(fps) if fps else 0.0
    lines = ["VIDEO FRAME PICKER", "%s: frame %d (last frame %d), %.3f s, %.3f fps, %dx%d" % (name, index, total - 1, seconds, fps, width, height)]
    if note:
        lines.append(note)
    return "\n".join(lines)


def video_info(path):
    """Frame rate, frame count, length and size of a video file, read with PyAV. No pictures are decoded
    unless the file does not say how many frames it has."""
    import av
    with av.open(path) as box:
        if not box.streams.video:
            raise ValueError("this file has no video track: %s" % os.path.basename(path))
        st = box.streams.video[0]
        fps = float(st.average_rate or st.guessed_rate or 0)
        if fps <= 0:
            raise ValueError("this video has no frame rate: %s" % os.path.basename(path))
        frames = int(st.frames or 0)
        seconds = 0.0
        if st.duration is not None and st.time_base is not None:
            seconds = float(st.duration * st.time_base)
        elif box.duration:
            seconds = box.duration / 1_000_000.0
        if frames <= 0:   # some files (webm, mkv) do not store the count: count the packets
            frames = sum(1 for p in box.demux(st) if p.size)
        if seconds <= 0:
            seconds = frames / fps
        return {"fps": fps, "frames": frames, "seconds": seconds, "width": int(st.codec_context.width),
                "height": int(st.codec_context.height)}


def decode_frame(path, index, fps):
    """The picture of frame `index` as an RGB numpy array (height, width, 3), read with PyAV. It jumps to the nearest
    key frame before the wanted time and decodes from there, so long videos stay fast."""
    import av
    with av.open(path) as box:
        st = box.streams.video[0]
        tb = float(st.time_base)
        start = float(st.start_time * st.time_base) if st.start_time is not None else 0.0
        target = start + index / float(fps)
        if index > 0:
            box.seek(max(0, int((target - start) / tb) + (st.start_time or 0)), stream=st, backward=True, any_frame=False)
        last = None
        for fr in box.decode(st):
            if fr.pts is None:
                continue
            last = fr
            if frame_of_time(fr.pts * tb - start, fps) >= index:
                return fr.to_ndarray(format="rgb24")
        if last is None:
            raise ValueError("no picture could be read near frame %d" % index)
        return last.to_ndarray(format="rgb24")   # asked past the real end: the last frame


def _input_names():
    try:
        import folder_paths
        return os.listdir(folder_paths.get_input_directory())
    except Exception:
        return []


class SYVideoFramePicker:
    DESCRIPTION = ("Shows a video in the node with a timeline slider. Scrub (or use the -1 / +1 buttons) to the frame you "
                   "want and leave the slider there: when you run the workflow, that frame comes out as a picture.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("image", "frame", "seconds", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": (pick_videos(_input_names()), {"video_upload": True, "tooltip": "A video from the input folder. You can also upload one."}),
                "frame": ("INT", {"default": 0, "min": 0, "max": MAX_FRAME, "tooltip": "Frame number to export (0 = first). Set it with the slider on the node."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, video, frame):
        try:
            import folder_paths
            return "%s|%s|%d" % (video, os.path.getmtime(folder_paths.get_annotated_filepath(video)), int(frame))
        except Exception:
            return "%s|%s" % (video, frame)

    def run(self, video, frame):
        if video == NONE:
            raise ValueError("pick a video first (or upload one)")
        import folder_paths
        import numpy as np
        import torch
        path = folder_paths.get_annotated_filepath(video)
        if not os.path.isfile(path):
            raise ValueError("video not found in the input folder: %s" % video)
        meta = video_info(path)
        index, note = clamp_frame(frame, meta["frames"])
        pic = decode_frame(path, index, meta["fps"])
        image = torch.from_numpy(np.ascontiguousarray(pic).astype(np.float32) / 255.0)[None, ]
        seconds = index / meta["fps"]
        info = info_text(video, index, meta["frames"], meta["fps"], pic.shape[1], pic.shape[0], note)
        return (image, index, seconds, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoFramePicker", SYVideoFramePicker)
NODE_DISPLAY_NAME_MAPPINGS["SYVideoFramePicker"] = "Video Frame Picker SY"
