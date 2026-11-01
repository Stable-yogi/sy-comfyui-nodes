"""Mask Grow Shrink SY: makes the white part of a mask bigger or smaller by a number of pixels."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
    from ._sy_d3_info import pct_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm
    from _sy_d3_info import pct_text

SHAPES = ("round", "square")


def grow_shrink(rows, pixels, shape="round"):
    """Pure function on a nested-list mask [H][W]. Positive grows, negative shrinks."""
    return mm.grow_shrink_list(rows, int(pixels), shape)


def grow_shrink_info(pixels, shape, before, after, total):
    """Pure function. Plain sentence: what was done and how much white there is before and after (counts of white pixels)."""
    pixels = int(pixels)
    if pixels == 0:
        return "Pixels is 0: the mask was passed through unchanged (white %s)." % pct_text(before, total)
    what = ("Grew" if pixels > 0 else "Shrunk") + " the white area by %d px (%s brush)" % (abs(pixels), shape)
    text = "%s: white went from %s to %s of the mask." % (what, pct_text(before, total), pct_text(after, total))
    if before == 0:
        text += " The input mask was empty, so there was nothing to change."
    elif after == 0:
        text += " Nothing white is left: use a smaller negative number."
    elif after == total:
        text += " The whole mask is white now: use a smaller number."
    return text


class SYMaskGrowShrink:
    DESCRIPTION = "Makes the white area of a mask bigger (positive pixels) or smaller (negative pixels). The info output says how much white there was before and after, and warns when the mask became empty or full."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "STRING")
    RETURN_NAMES = ("mask", "info")

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
        m = mm.t_mask3(mask)
        if m.shape[0] < 1:
            raise ValueError("the mask batch is empty: connect at least 1 mask")
        out = mm.t_grow_shrink(m, int(pixels), shape)
        total = int(out.numel())
        before = int((m >= 0.5).sum())
        after = int((out >= 0.5).sum())
        return (out, grow_shrink_info(pixels, shape, before, after, total))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskGrowShrink", SYMaskGrowShrink)
