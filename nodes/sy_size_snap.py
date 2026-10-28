"""Size Snap SY: snap a width and height to a multiple."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("nearest", "up", "down")
MAX_SIDE = 65536


def snap_value(value, multiple, mode):
    """Pure function. Snap one number to a multiple. Result is never below one multiple."""
    value, multiple = int(value), int(multiple)
    if mode not in MODES:
        raise ValueError("unknown mode %r, pick one of: %s" % (mode, ", ".join(MODES)))
    if multiple < 1:
        raise ValueError("multiple must be at least 1, got %d" % multiple)
    if value < 1:
        raise ValueError("size must be at least 1, got %d" % value)
    if mode == "up":
        out = -(-value // multiple) * multiple
    elif mode == "down":
        out = (value // multiple) * multiple
    else:
        out = ((2 * value + multiple) // (2 * multiple)) * multiple  # halves go up
    return max(multiple, out)


def snap_size(width, height, multiple, mode):
    """Pure function. Returns (w, h) snapped to `multiple`."""
    return (snap_value(width, multiple, mode), snap_value(height, multiple, mode))


class SYSizeSnap:
    DESCRIPTION = ("Snaps a width and height to a multiple, like 8 or 64, so a model accepts them. "
                   "Pick nearest, round up or round down.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1000, "min": 1, "max": MAX_SIDE, "tooltip": "Width in pixels to snap."}),
                "height": ("INT", {"default": 1000, "min": 1, "max": MAX_SIDE, "tooltip": "Height in pixels to snap."}),
                "multiple": ("INT", {"default": 8, "min": 1, "max": 1024, "tooltip": "Snap to a multiple of this number."}),
                "mode": (list(MODES), {"default": "nearest", "tooltip": "Nearest rounds either way. Up never shrinks. Down never grows."}),
            }
        }

    def run(self, width, height, multiple, mode):
        return snap_size(width, height, multiple, mode)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SizeSnap", SYSizeSnap)
NODE_DISPLAY_NAME_MAPPINGS["SYSizeSnap"] = "Size Snap SY"
