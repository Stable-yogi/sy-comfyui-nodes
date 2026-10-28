"""Duration Frames SY: converts seconds to frames, or frames to seconds, for a given frame rate."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("seconds_to_frames", "frames_to_seconds")


def convert(mode, seconds, frames, fps):
    """Pure function. Returns (frames, seconds, info)."""
    fps = float(fps)
    if not fps > 0:
        raise ValueError("fps must be greater than 0, got %s" % fps)
    if mode == "seconds_to_frames":
        seconds = float(seconds)
        if seconds < 0:
            raise ValueError("seconds must not be negative, got %s" % seconds)
        frames = int(seconds * fps + 0.5)
    elif mode == "frames_to_seconds":
        frames = int(frames)
        if frames < 0:
            raise ValueError("frames must not be negative, got %d" % frames)
        seconds = frames / fps
    else:
        raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))
    info = "%d frames = %.3f seconds at %s fps" % (frames, seconds, fps)
    return frames, seconds, info


class SYDurationFrames:
    DESCRIPTION = "Turns seconds into a frame count, or a frame count into seconds, using the frame rate you give."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "STRING")
    RETURN_NAMES = ("frames", "seconds", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (list(MODES), {"default": "seconds_to_frames", "tooltip": "Which way to convert."}),
                "seconds": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 100000.0, "step": 0.01, "tooltip": "Length in seconds. Used when mode is seconds_to_frames."}),
                "frames": ("INT", {"default": 120, "min": 0, "max": 10000000, "tooltip": "Frame count. Used when mode is frames_to_seconds."}),
                "fps": ("FLOAT", {"default": 24.0, "min": 0.01, "max": 1000.0, "step": 0.01, "tooltip": "Frames per second."}),
            }
        }

    def run(self, mode, seconds, frames, fps):
        return convert(mode, seconds, frames, fps)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DurationFrames", SYDurationFrames)
NODE_DISPLAY_NAME_MAPPINGS["SYDurationFrames"] = "Duration Frames SY"
