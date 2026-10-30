"""H3 Length SY: turns seconds into a frame count the video model accepts."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

ROUNDS = ("up", "nearest", "down")
GRID_STEP = 17
GRID_OFFSET = 5
MIN_FRAMES = 5


def frames_for(seconds, fps=24, rounding="up"):
    """Pure function. Returns (frames, real_seconds, info). frames is one of 5, 22, 39 ... (17 * k + 5)."""
    if rounding not in ROUNDS:
        raise ValueError("rounding must be one of: %s" % ", ".join(ROUNDS))
    seconds = float(seconds)
    fps = int(fps)
    if seconds <= 0:
        raise ValueError("seconds must be more than 0")
    if fps < 1:
        raise ValueError("fps must be at least 1")
    raw = seconds * fps
    x = (raw - GRID_OFFSET) / GRID_STEP
    if rounding == "up":
        k = math.ceil(x - 1e-9)
    elif rounding == "down":
        k = math.floor(x + 1e-9)
    else:
        k = int(math.floor(x + 0.5))
    k = max(0, k)
    frames = k * GRID_STEP + GRID_OFFSET
    real = round(frames / float(fps), 3)
    info = "%.2f s at %d fps = %d wanted, %s -> %d frames (%.2f s)" % (seconds, fps, round(raw), rounding, frames, real)
    return frames, real, info


class SYH3Length:
    DESCRIPTION = ("Turns seconds into a frame count the video model accepts. The model only takes 5, 22, 39, 56 ... frames "
                   "(17 times a whole number, plus 5). 124 frames is about 5 seconds at 24 per second.")
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "STRING")
    RETURN_NAMES = ("frames", "real_seconds", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seconds": ("FLOAT", {"default": 5.0, "min": 0.1, "max": 150.0, "step": 0.1, "tooltip": "How long the clip should be."}),
                "fps": ("INT", {"default": 24, "min": 1, "max": 120, "tooltip": "Frames per second. The video model makes 24."}),
                "rounding": (list(ROUNDS), {"default": "up", "tooltip": "up keeps the whole time you asked for. nearest and down can make the clip a little shorter."}),
            }
        }

    def run(self, seconds, fps, rounding):
        return frames_for(seconds, fps, rounding)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3Length", SYH3Length)
NODE_DISPLAY_NAME_MAPPINGS["SYH3Length"] = "H3 Length SY"
