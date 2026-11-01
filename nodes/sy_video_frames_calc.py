"""Video Frames Calc SY: how many frames a clip of some seconds needs at some frame rate."""
try:
    from ._sy_common import category, register
    from ._sy_a2_video import ROUNDINGS, snap_frames
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_a2_video import ROUNDINGS, snap_frames

MAX_FRAMES = 1_000_000


def calc_frames(seconds, fps, four_n_plus_one, frame_step=4, rounding="nearest"):
    """Pure function. Returns (frames, fps, seconds_real).

    frames = round(seconds * fps), at least 1. With four_n_plus_one the count is moved to the nearest
    value of the form 4n+1 (1, 5, 9, 13 ...), as many video models need. seconds_real = frames / fps.
    frame_step changes the 4 (use 8 for 8n+1 models). rounding says nearest, up (never shorter) or down (never longer).
    """
    seconds, fps = float(seconds), float(fps)
    if not (0 < seconds <= 100000):  # also rejects nan
        raise ValueError("seconds must be above 0 and at most 100000, got %s" % seconds)
    if not (0 < fps <= 1000):
        raise ValueError("fps must be above 0 and at most 1000, got %s" % fps)
    frames = max(1, int(seconds * fps + 0.5))
    if four_n_plus_one:
        frames = snap_frames(frames, frame_step, rounding)
    if frames > MAX_FRAMES:
        raise ValueError("that is %d frames, more than the limit of %d. Lower seconds or fps" % (frames, MAX_FRAMES))
    return (frames, fps, frames / fps)


def calc_info(seconds, fps, frames, real_seconds, four_n_plus_one, frame_step=4):
    """Pure function. One plain line: what was asked, the frame count, and the real length."""
    plain = max(1, int(float(seconds) * float(fps) + 0.5))
    text = "%g s x %g fps = %d frames" % (float(seconds), float(fps), plain)
    if four_n_plus_one and plain != frames:
        text += ", moved to %d to fit the %dn+1 rule" % (frames, int(frame_step))
    elif four_n_plus_one:
        text += ", already fits the %dn+1 rule" % int(frame_step)
    return text + ". Real length: %.3f s." % real_seconds


class SYVideoFramesCalc:
    DESCRIPTION = ("Turns seconds and frames per second into a frame count. "
                   "Switch on 4n+1 to land on 1, 5, 9, 13 ... frames, which many video models need. "
                   "Pick the step (8 for LTX) and whether to round to the nearest, round up so the clip is never shorter, or round down. "
                   "The info output shows what was asked and the real length.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "FLOAT", "STRING")
    RETURN_NAMES = ("frames", "fps", "seconds", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seconds": ("FLOAT", {"default": 5.0, "min": 0.01, "max": 100000.0, "step": 0.1, "tooltip": "How long the clip should be, in seconds."}),
                "fps": ("FLOAT", {"default": 16.0, "min": 0.1, "max": 1000.0, "step": 1.0, "tooltip": "Frames per second of the clip."}),
                "four_n_plus_one": ("BOOLEAN", {"default": True, "tooltip": "On makes the frame count 4n+1 (like 81). Off keeps the plain count."}),
            },
            "optional": {
                "frame_step": ("INT", {"default": 4, "min": 1, "max": 64, "tooltip": "The n in the Kn+1 rule: 4 for Wan and most models, 8 for LTX. Only used when the switch is on."}),
                "rounding": (ROUNDINGS, {"default": "nearest", "tooltip": "nearest: closest valid count. up: never shorter than asked. down: never longer."}),
            },
        }

    def run(self, seconds, fps, four_n_plus_one, frame_step=4, rounding="nearest"):
        frames, rate, real = calc_frames(seconds, fps, bool(four_n_plus_one), frame_step, rounding)
        return (frames, rate, real, calc_info(seconds, fps, frames, real, bool(four_n_plus_one), frame_step))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoFramesCalc", SYVideoFramesCalc)
NODE_DISPLAY_NAME_MAPPINGS["SYVideoFramesCalc"] = "Video Frames Calc SY"
