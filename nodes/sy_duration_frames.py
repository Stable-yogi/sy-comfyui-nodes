"""Duration Frames SY: converts seconds to frames, or frames to seconds, for a given frame rate."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("seconds_to_frames", "frames_to_seconds")
FRAME_RULES = ("none", "4n+1", "8n+1", "16n+1")


def convert(mode, seconds, frames, fps, frame_rule="none"):
    """Pure function. Returns (frames, seconds, info)."""
    fps = float(fps)
    if frame_rule not in FRAME_RULES:
        raise ValueError("frame_rule must be one of %s, got %r" % (", ".join(FRAME_RULES), frame_rule))
    step = 0 if frame_rule == "none" else int(frame_rule.split("n")[0])
    note = ""
    if not fps > 0:
        raise ValueError("fps must be greater than 0, got %s" % fps)
    if mode == "seconds_to_frames":
        seconds = float(seconds)
        if seconds < 0:
            raise ValueError("seconds must not be negative, got %s" % seconds)
        frames = int(seconds * fps + 0.5)
        if step:
            snapped = max(1, int((frames - 1) / step + 0.5)) * step + 1
            if snapped != frames:
                note = ", snapped from %d to fit the %s video rule" % (frames, frame_rule)
            frames = snapped
            seconds = frames / fps
    elif mode == "frames_to_seconds":
        frames = int(frames)
        if frames < 0:
            raise ValueError("frames must not be negative, got %d" % frames)
        seconds = frames / fps
        if step and (frames - 1) % step:
            note = ", note: %d does not fit the %s video rule" % (frames, frame_rule)
    else:
        raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))
    info = "%d frames = %.3f seconds at %s fps%s" % (frames, seconds, fps, note)
    return frames, seconds, info


class SYDurationFrames:
    DESCRIPTION = "Turns seconds into a frame count, or a frame count into seconds, using the frame rate you give. The optional frame rule (4n+1 and so on) snaps the count to what video models accept and says so in the info line."
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
            },
            "optional": {
                "frame_rule": (list(FRAME_RULES), {"default": "none", "tooltip": "4n+1 snaps the frame count to 5, 9, 13... as many video models need."}),
            },
        }

    def run(self, mode, seconds, frames, fps, frame_rule="none"):
        return convert(mode, seconds, frames, fps, frame_rule)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DurationFrames", SYDurationFrames)
NODE_DISPLAY_NAME_MAPPINGS["SYDurationFrames"] = "Duration Frames SY"
