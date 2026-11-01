"""Mask Combine SY: joins two masks with union, intersect, subtract or xor."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
    from . import _sy_d2_common as d2
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm
    import _sy_d2_common as d2

OPS = ("union", "intersect", "subtract", "xor")


def combine(a, b, op, grow=0, feather=0, invert=False):
    """Pure function on nested-list masks [H][W]. b is stretched to the size of a when needed.
    Optional clean-up after the combine, always in this order: grow (or shrink), then feather, then invert."""
    if op not in OPS:
        raise ValueError("unknown combine operation: %r (use %s)" % (op, ", ".join(OPS)))
    check_cleanup(grow, feather)
    out = mm.combine_list(a, b, op)
    if grow:
        out = mm.grow_shrink_list(out, int(grow))
    if feather:
        out = mm.blur_list(out, int(feather))
    if invert:
        out = [[1.0 - v for v in r] for r in out]
    return out


def check_cleanup(grow, feather):
    if abs(grow) > mm.MAX_RADIUS:
        raise ValueError("grow must be between -%d and %d pixels, got %s" % (mm.MAX_RADIUS, mm.MAX_RADIUS, grow))
    if feather < 0 or feather > mm.MAX_RADIUS:
        raise ValueError("feather must be between 0 and %d pixels, got %s" % (mm.MAX_RADIUS, feather))


def combine_info(op, size_a, size_b, batch_a, batch_b, pct_a, pct_b, pct_result, grow=0, feather=0, invert=False):
    """Pure function. One plain line: what was combined, size and batch mismatches, and an empty-result warning."""
    parts = ["%s of A (%s) and B (%s)" % (op, d2.coverage_text(pct_a), d2.coverage_text(pct_b))]
    if size_a != size_b:
        parts.append("B was %s and was stretched to the size of A (%s)" % (d2.size_text(*size_b), d2.size_text(*size_a)))
    if batch_b > batch_a:
        parts.append("B has %d masks but A has %d, so only the first %d of B were used" % (batch_b, batch_a, batch_a))
    after = []
    if grow:
        after.append("%s %d px" % ("grown" if grow > 0 else "shrunk", abs(grow)))
    if feather:
        after.append("feathered %d px" % feather)
    if invert:
        after.append("inverted")
    if after:
        parts.append("then " + ", then ".join(after) + " (grow always comes before feather)")
    text = "; ".join(parts)
    text = text[0].upper() + text[1:] + ". Result: " + d2.coverage_text(pct_result)
    if pct_result <= 0.0 and not (pct_a <= 0.0 and pct_b <= 0.0):
        text += ". The result is empty: " + {
            "intersect": "the two masks do not overlap",
            "subtract": "B covers all of A",
            "xor": "the two masks are the same",
        }.get(op, "check the masks")
    elif pct_a <= 0.0 and pct_b <= 0.0:
        text += ". Both input masks are empty"
    return text + "."


class SYMaskCombine:
    DESCRIPTION = ("Joins two masks: union (either), intersect (both), subtract (A without B) or xor (only one). B is resized to A. "
                   "Can also grow or shrink, then feather, then invert the result in the right order. The info line warns about empty masks and size mismatches.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "STRING")
    RETURN_NAMES = ("mask", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask_a": ("MASK", {"tooltip": "The first mask. Its size sets the result size."}),
                "mask_b": ("MASK", {"tooltip": "The second mask. It is stretched to the size of mask A if needed."}),
                "operation": (list(OPS), {"default": "union", "tooltip": "union = A or B, intersect = A and B, subtract = A minus B, xor = in one only."}),
            },
            "optional": {
                "grow": ("INT", {"default": 0, "min": -mm.MAX_RADIUS, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "After combining: grow the white area by this many pixels (negative shrinks). 0 is off."}),
                "feather": ("INT", {"default": 0, "min": 0, "max": mm.MAX_RADIUS, "step": 1, "tooltip": "After growing: soften the edge by this many pixels. 0 is off."}),
                "invert_result": ("BOOLEAN", {"default": False, "tooltip": "Swap white and black in the finished mask."}),
            },
        }

    def run(self, mask_a, mask_b, operation, grow=0, feather=0, invert_result=False):
        if operation not in OPS:
            raise ValueError("unknown combine operation: %r (use %s)" % (operation, ", ".join(OPS)))
        check_cleanup(grow, feather)
        a, b = mm.t_mask3(mask_a), mm.t_mask3(mask_b)
        out = mm.t_combine(a, b, operation)
        if grow:
            out = mm.t_grow_shrink(out, int(grow))
        if feather:
            out = mm.t_blur(out, int(feather))
        if invert_result:
            out = 1.0 - out
        info = combine_info(operation, (a.shape[2], a.shape[1]), (b.shape[2], b.shape[1]), a.shape[0], b.shape[0],
                            100.0 * float(a.mean()), 100.0 * float(b.mean()), 100.0 * float(out.mean()),
                            int(grow), int(feather), bool(invert_result))
        return (out.contiguous(), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskCombine", SYMaskCombine)
