"""Video Frames Calc SY: how many frames a clip of some seconds needs at some frame rate."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_FRAMES = 1_000_000


def calc_frames(seconds, fps, four_n_plus_one):
    """Pure function. Returns (frames, fps, seconds_real).

    frames = round(seconds * fps), at least 1. With four_n_plus_one the count is moved to the nearest
    value of the form 4n+1 (1, 5, 9, 13 ...), as many video models need. seconds_real = frames / fps.
    """
    seconds, fps = float(seconds), float(fps)
    if not (0 < seconds <= 100000):  # also rejects nan
        raise ValueError("seconds must be above 0 and at most 100000, got %s" % seconds)
    if not (0 < fps <= 1000):
        raise ValueError("fps must be above 0 and at most 1000, got %s" % fps)
    frames = max(1, int(seconds * fps + 0.5))
    if four_n_plus_one:
        frames = 4 * int((frames - 1) / 4 + 0.5) + 1
    if frames > MAX_FRAMES:
        raise ValueError("that is %d frames, more than the limit of %d. Lower seconds or fps" % (frames, MAX_FRAMES))
    return (frames, fps, frames / fps)


class SYVideoFramesCalc:
    DESCRIPTION = ("Turns seconds and frames per second into a frame count. "
                   "Switch on 4n+1 to land on 1, 5, 9, 13 ... frames, which many video models need.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("frames", "fps", "seconds")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seconds": ("FLOAT", {"default": 5.0, "min": 0.01, "max": 100000.0, "step": 0.1, "tooltip": "How long the clip should be, in seconds."}),
                "fps": ("FLOAT", {"default": 16.0, "min": 0.1, "max": 1000.0, "step": 1.0, "tooltip": "Frames per second of the clip."}),
                "four_n_plus_one": ("BOOLEAN", {"default": True, "tooltip": "On makes the frame count 4n+1 (like 81). Off keeps the plain count."}),
            }
        }

    def run(self, seconds, fps, four_n_plus_one):
        return calc_frames(seconds, fps, bool(four_n_plus_one))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoFramesCalc", SYVideoFramesCalc)
NODE_DISPLAY_NAME_MAPPINGS["SYVideoFramesCalc"] = "Video Frames Calc SY"
