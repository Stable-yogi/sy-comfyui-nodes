"""Time Code SY: converts a frame number to HH:MM:SS:FF and back."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("frame_to_timecode", "timecode_to_frame")


def _base(fps):
    fps = float(fps)
    if not fps > 0:
        raise ValueError("fps must be greater than 0, got %s" % fps)
    nominal = int(fps + 0.5)
    if nominal < 1:
        raise ValueError("fps must be at least 1 for a time code, got %s" % fps)
    return fps, nominal


def frame_to_timecode(frame, fps):
    """Returns HH:MM:SS:FF. The FF part counts whole frames per second (no drop frame)."""
    fps, nominal = _base(fps)
    frame = int(frame)
    if frame < 0:
        raise ValueError("frame must not be negative, got %d" % frame)
    ff = frame % nominal
    total = frame // nominal
    return "%02d:%02d:%02d:%02d" % (total // 3600, (total // 60) % 60, total % 60, ff)


def timecode_to_frame(code, fps):
    """Parses HH:MM:SS:FF and returns the frame number."""
    fps, nominal = _base(fps)
    parts = str(code).strip().split(":")
    if len(parts) != 4 or not all(p.isascii() and p.isdigit() for p in parts):
        raise ValueError("time code must look like HH:MM:SS:FF, got %r" % code)
    h, m, s, ff = (int(p) for p in parts)
    if m > 59 or s > 59:
        raise ValueError("minutes and seconds must be 0 to 59 in %r" % code)
    if ff >= nominal:
        raise ValueError("frame part must be below %d at %s fps in %r" % (nominal, fps, code))
    return ((h * 60 + m) * 60 + s) * nominal + ff


def convert(mode, frame, fps, timecode):
    """Returns (timecode, seconds, frame)."""
    fps, _ = _base(fps)
    if mode == "frame_to_timecode":
        frame = int(frame)
        code = frame_to_timecode(frame, fps)
    elif mode == "timecode_to_frame":
        frame = timecode_to_frame(timecode, fps)
        code = frame_to_timecode(frame, fps)
    else:
        raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))
    return code, frame / fps, frame


class SYTimeCode:
    DESCRIPTION = "Turns a frame number into a time code like 00:00:03:12, or reads a time code back into a frame number."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "FLOAT", "INT")
    RETURN_NAMES = ("timecode", "seconds", "frame")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (list(MODES), {"default": "frame_to_timecode", "tooltip": "Which way to convert."}),
                "frame": ("INT", {"default": 0, "min": 0, "max": 100000000, "tooltip": "Frame number. Used when mode is frame_to_timecode."}),
                "fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 1000.0, "step": 0.01, "tooltip": "Frames per second."}),
                "timecode": ("STRING", {"default": "00:00:00:00", "tooltip": "Time code as HH:MM:SS:FF. Used when mode is timecode_to_frame."}),
            }
        }

    def run(self, mode, frame, fps, timecode):
        return convert(mode, frame, fps, timecode)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TimeCode", SYTimeCode)
NODE_DISPLAY_NAME_MAPPINGS["SYTimeCode"] = "Time Code SY"
