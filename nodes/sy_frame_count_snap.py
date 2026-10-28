"""Frame Count Snap SY: rounds a wanted frame count to a multiple of a step, optionally plus one."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("nearest", "down", "up")


def snap_frames(wanted, step=4, mode="nearest", plus_one=True):
    """Pure function. Returns (frames, info). The base is a multiple of step, at least one step."""
    wanted = int(wanted)
    step = int(step)
    if wanted < 1:
        raise ValueError("wanted_frames must be at least 1, got %d" % wanted)
    if step < 1:
        raise ValueError("step must be at least 1, got %d" % step)
    if mode not in MODES:
        raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))
    if mode == "down":
        base = (wanted // step) * step
    elif mode == "up":
        base = -(-wanted // step) * step
    else:
        base = ((2 * wanted + step) // (2 * step)) * step  # halves round up
    if base < step:
        base = step
    frames = base + 1 if plus_one else base
    info = "wanted %d, step %d, %s -> %d%s = %d frames" % (
        wanted, step, mode, base, " +1" if plus_one else "", frames)
    return frames, info


class SYFrameCountSnap:
    DESCRIPTION = "Rounds a wanted frame count to a multiple of a step, then can add one frame. Example: 80 with step 4 gives 81."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("frames", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "wanted_frames": ("INT", {"default": 80, "min": 1, "max": 100000, "tooltip": "The number of frames you would like."}),
                "step": ("INT", {"default": 4, "min": 1, "max": 1024, "tooltip": "The result is a multiple of this number."}),
                "mode": (list(MODES), {"default": "nearest", "tooltip": "nearest picks the closest multiple, down rounds lower, up rounds higher."}),
                "plus_one": ("BOOLEAN", {"default": True, "tooltip": "Add one extra frame after snapping (for example 80 becomes 81)."}),
            }
        }

    def run(self, wanted_frames, step, mode, plus_one):
        frames, info = snap_frames(wanted_frames, step, mode, plus_one)
        return (frames, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FrameCountSnap", SYFrameCountSnap)
NODE_DISPLAY_NAME_MAPPINGS["SYFrameCountSnap"] = "Frame Count Snap SY"
