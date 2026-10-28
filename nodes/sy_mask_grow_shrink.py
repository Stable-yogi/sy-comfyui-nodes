"""Mask Grow Shrink SY: makes the white part of a mask bigger or smaller by a number of pixels."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm

SHAPES = ("round", "square")


def grow_shrink(rows, pixels, shape="round"):
    """Pure function on a nested-list mask [H][W]. Positive grows, negative shrinks."""
    return mm.grow_shrink_list(rows, int(pixels), shape)


class SYMaskGrowShrink:
    DESCRIPTION = "Makes the white area of a mask bigger (positive pixels) or smaller (negative pixels)."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask to change."}),
                "pixels": ("INT", {"default": 8, "min": -mm.MAX_RADIUS, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "Positive grows the white area, negative shrinks it."}),
                "shape": (list(SHAPES), {"default": "round", "tooltip": "Round keeps corners smooth. Square grows corners out."}),
            }
        }

    def run(self, mask, pixels, shape):
        return (mm.t_grow_shrink(mm.t_mask3(mask), int(pixels), shape),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskGrowShrink", SYMaskGrowShrink)
