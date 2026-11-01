"""Size Snap SY: snap a width and height to a multiple."""
try:
    from ._sy_common import category, register
    from ._sy_b_sizeinfo import size_facts
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_b_sizeinfo import size_facts

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


def snap_size(width, height, multiple, mode, max_megapixels=0.0):
    """Pure function. Returns (w, h) snapped to `multiple`.
    max_megapixels above 0 is a memory-safety cap: a result over it is scaled down (same shape) and snapped down."""
    w, h = snap_value(width, multiple, mode), snap_value(height, multiple, mode)
    cap = float(max_megapixels)
    if not cap >= 0:
        raise ValueError("max_megapixels must be 0 (off) or more, got %s" % cap)
    if cap > 0 and w * h > cap * 1_000_000:
        m = int(multiple)
        if m * m > cap * 1_000_000:
            raise ValueError("max_megapixels %g is too small: even %dx%d is over it. Raise it or lower multiple." % (cap, m, m))
        scale = (cap * 1_000_000 / (w * h)) ** 0.5
        w, h = max(m, int(w * scale) // m * m), max(m, int(h * scale) // m * m)
    return (w, h)


def snap_report(width, height, multiple, mode, max_megapixels=0.0):
    """Pure function. Returns (w, h, info). The info line also says how much the shape moved."""
    w, h = snap_size(width, height, multiple, mode, max_megapixels)
    width, height = int(width), int(height)
    shift = abs((w / h) / (width / height) - 1.0) * 100.0
    info = "%dx%d -> %dx%d (%s, multiple of %d, %s)" % (width, height, w, h, mode, int(multiple), size_facts(w, h).split(", ", 1)[0])
    if (w, h) == (width, height):
        info = "%dx%d already fits a multiple of %d, kept" % (width, height, int(multiple))
    elif shift >= 0.05:
        info += ", shape changed by %.1f%%" % shift
    if float(max_megapixels) > 0 and (w, h) != snap_size(width, height, multiple, mode):
        info += ", lowered to stay under %g MP" % float(max_megapixels)
    return w, h, info


class SYSizeSnap:
    DESCRIPTION = "Snaps a width and height to a multiple, like 8 or 64, so a model accepts them. Pick nearest, round up or round down. The info line shows what changed and how much the shape moved. An optional megapixel cap stops a round-up from going over your memory."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1000, "min": 1, "max": MAX_SIDE, "tooltip": "Width in pixels to snap."}),
                "height": ("INT", {"default": 1000, "min": 1, "max": MAX_SIDE, "tooltip": "Height in pixels to snap."}),
                "multiple": ("INT", {"default": 8, "min": 1, "max": 1024, "tooltip": "Snap to a multiple of this number."}),
                "mode": (list(MODES), {"default": "nearest", "tooltip": "Nearest rounds either way. Up never shrinks. Down never grows."}),
            },
            "optional": {
                "max_megapixels": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 4096.0, "step": 0.1, "tooltip": "0 is off. Example: 2.0 makes sure the snapped size stays under 2 million pixels."}),
            },
        }

    def run(self, width, height, multiple, mode, max_megapixels=0.0):
        return snap_report(width, height, multiple, mode, max_megapixels)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SizeSnap", SYSizeSnap)
NODE_DISPLAY_NAME_MAPPINGS["SYSizeSnap"] = "Size Snap SY"
