"""Swap Width Height SY: swap the two sizes, or pass them through, with one switch."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SIDE = 65536


FORCE = ("use_swap_switch", "landscape", "portrait")


def swap_size(width, height, swap, force="use_swap_switch"):
    """Pure function. Returns (height, width) when swap is true, else (width, height).
    force landscape or portrait ignores the switch and puts the longer side where it belongs."""
    width, height = int(width), int(height)
    if width < 0 or height < 0:
        raise ValueError("width and height cannot be negative, got %dx%d" % (width, height))
    if not isinstance(swap, bool):
        raise ValueError("swap must be true or false, got %r" % (swap,))
    if force not in FORCE:
        raise ValueError("force must be one of: %s, got %r" % (", ".join(FORCE), force))
    if force == "landscape":
        return (max(width, height), min(width, height))
    if force == "portrait":
        return (min(width, height), max(width, height))
    return (height, width) if swap else (width, height)


def swap_report(width, height, swap, force="use_swap_switch"):
    """Pure function. Returns (width, height, info)."""
    w, h = swap_size(width, height, swap, force)
    width, height = int(width), int(height)
    if (w, h) == (width, height):
        why = "kept" if force == "use_swap_switch" else "already %s, kept" % force
        return w, h, "%dx%d %s" % (width, height, why)
    return w, h, "%dx%d -> %dx%d (swapped%s)" % (width, height, w, h, "" if force == "use_swap_switch" else " to make it %s" % force)


class SYSwapWidthHeight:
    DESCRIPTION = "Swaps width and height when the switch is on. Turns a landscape size into portrait and back. Choose force landscape or force portrait to always get the shape you want, whatever size comes in. The info line says what happened."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 0, "max": MAX_SIDE, "tooltip": "Width in pixels."}),
                "height": ("INT", {"default": 768, "min": 0, "max": MAX_SIDE, "tooltip": "Height in pixels."}),
                "swap": ("BOOLEAN", {"default": True, "tooltip": "On swaps the two sizes. Off passes them through unchanged."}),
            },
            "optional": {
                "force": (list(FORCE), {"default": "use_swap_switch", "tooltip": "landscape or portrait puts the longer side where it belongs, whatever the switch says."}),
            },
        }

    def run(self, width, height, swap, force="use_swap_switch"):
        return swap_report(width, height, bool(swap), force)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SwapWidthHeight", SYSwapWidthHeight)
NODE_DISPLAY_NAME_MAPPINGS["SYSwapWidthHeight"] = "Swap Width Height SY"
