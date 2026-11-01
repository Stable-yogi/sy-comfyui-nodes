"""Frame Count Snap SY: rounds a wanted frame count to a multiple of a step, optionally plus one."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("nearest", "down", "up")


def snap_frames(wanted, step=4, mode="nearest", plus_one=True, max_frames=0):
    """Pure function. Returns (frames, info). The base is a multiple of step, at least one step.
    max_frames above 0 is a memory-safety cap: the answer is lowered to the biggest allowed count at or under it."""
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
    extra = 1 if plus_one else 0
    capped = ""
    max_frames = int(max_frames)
    if max_frames > 0 and base + extra > max_frames:
        base = ((max_frames - extra) // step) * step
        if base < step:
            raise ValueError("max_frames %d is too small: the smallest allowed count is %d. Raise max_frames." % (max_frames, step + extra))
        capped = ", capped by max_frames %d" % max_frames
    frames = base + extra
    info = "wanted %d, step %d, %s -> %d%s = %d frames%s" % (
        wanted, step, mode, base, " +1" if plus_one else "", frames, capped)
    return frames, info


class SYFrameCountSnap:
    DESCRIPTION = "Rounds a wanted frame count to a multiple of a step, then can add one frame. Example: 80 with step 4 gives 81. A max_frames cap keeps the clip small enough for your memory, and the seconds output shows the real length."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "STRING", "FLOAT")
    RETURN_NAMES = ("frames", "info", "seconds")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "wanted_frames": ("INT", {"default": 80, "min": 1, "max": 100000, "tooltip": "The number of frames you would like."}),
                "step": ("INT", {"default": 4, "min": 1, "max": 1024, "tooltip": "The result is a multiple of this number."}),
                "mode": (list(MODES), {"default": "nearest", "tooltip": "nearest picks the closest multiple, down rounds lower, up rounds higher."}),
                "plus_one": ("BOOLEAN", {"default": True, "tooltip": "Add one extra frame after snapping (for example 80 becomes 81)."}),
            },
            "optional": {
                "max_frames": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Safety cap against running out of memory. 0 is off. Example: 121."}),
                "fps": ("FLOAT", {"default": 24.0, "min": 0.01, "max": 1000.0, "step": 0.01, "tooltip": "Only used for the seconds output: frames divided by fps."}),
            },
        }

    def run(self, wanted_frames, step, mode, plus_one, max_frames=0, fps=24.0):
        if not float(fps) > 0:
            raise ValueError("fps must be greater than 0, got %s" % fps)
        frames, info = snap_frames(wanted_frames, step, mode, plus_one, max_frames)
        return (frames, info, frames / float(fps))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FrameCountSnap", SYFrameCountSnap)
NODE_DISPLAY_NAME_MAPPINGS["SYFrameCountSnap"] = "Frame Count Snap SY"
