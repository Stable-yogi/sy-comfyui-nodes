"""Swap Width Height SY: swap the two sizes, or pass them through, with one switch."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SIDE = 65536


def swap_size(width, height, swap):
    """Pure function. Returns (height, width) when swap is true, else (width, height)."""
    width, height = int(width), int(height)
    if width < 0 or height < 0:
        raise ValueError("width and height cannot be negative, got %dx%d" % (width, height))
    if not isinstance(swap, bool):
        raise ValueError("swap must be true or false, got %r" % (swap,))
    return (height, width) if swap else (width, height)


class SYSwapWidthHeight:
    DESCRIPTION = "Swaps width and height when the switch is on. Turns a landscape size into portrait and back."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 0, "max": MAX_SIDE, "tooltip": "Width in pixels."}),
                "height": ("INT", {"default": 768, "min": 0, "max": MAX_SIDE, "tooltip": "Height in pixels."}),
                "swap": ("BOOLEAN", {"default": True, "tooltip": "On swaps the two sizes. Off passes them through unchanged."}),
            }
        }

    def run(self, width, height, swap):
        return swap_size(width, height, bool(swap))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SwapWidthHeight", SYSwapWidthHeight)
NODE_DISPLAY_NAME_MAPPINGS["SYSwapWidthHeight"] = "Swap Width Height SY"
