"""Longest Side Scale SY: scale a size so its longest side hits a target, keeping the aspect."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SIDE = 65536


def _round_to(value, multiple):
    """Round to the nearest multiple (halves go up), never below one multiple."""
    return max(multiple, int(value / multiple + 0.5) * multiple)


def scale_longest_side(width, height, longest_side, multiple):
    """Pure function. Returns (w, h). The longer side becomes `longest_side` (rounded to `multiple`)."""
    width, height, longest_side, multiple = int(width), int(height), int(longest_side), int(multiple)
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1, got %dx%d" % (width, height))
    if longest_side < 1 or longest_side > MAX_SIDE:
        raise ValueError("longest_side must be between 1 and %d, got %d" % (MAX_SIDE, longest_side))
    if multiple < 1:
        raise ValueError("multiple must be at least 1, got %d" % multiple)
    long_out = _round_to(longest_side, multiple)
    if width >= height:
        w = long_out
        h = _round_to(long_out * height / width, multiple)
    else:
        h = long_out
        w = _round_to(long_out * width / height, multiple)
    return (w, h)


class SYLongestSideScale:
    DESCRIPTION = ("Works out a new width and height so the longer side equals the number you give. "
                   "The shape (aspect) stays the same. Both sides are rounded to a multiple.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Current width in pixels."}),
                "height": ("INT", {"default": 768, "min": 1, "max": MAX_SIDE, "tooltip": "Current height in pixels."}),
                "longest_side": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Size in pixels you want for the longer side."}),
                "multiple": ("INT", {"default": 8, "min": 1, "max": 256, "tooltip": "Both sides are rounded to a multiple of this. Use 1 for exact."}),
            }
        }

    def run(self, width, height, longest_side, multiple):
        return scale_longest_side(width, height, longest_side, multiple)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LongestSideScale", SYLongestSideScale)
NODE_DISPLAY_NAME_MAPPINGS["SYLongestSideScale"] = "Longest Side Scale SY"
