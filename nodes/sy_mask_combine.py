"""Mask Combine SY: joins two masks with union, intersect, subtract or xor."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm

OPS = ("union", "intersect", "subtract", "xor")


def combine(a, b, op):
    """Pure function on nested-list masks [H][W]. b is stretched to the size of a when needed."""
    if op not in OPS:
        raise ValueError("unknown combine operation: %r (use %s)" % (op, ", ".join(OPS)))
    return mm.combine_list(a, b, op)


class SYMaskCombine:
    DESCRIPTION = "Joins two masks: union (either), intersect (both), subtract (A without B) or xor (only one). B is resized to A."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask_a": ("MASK", {"tooltip": "The first mask. Its size sets the result size."}),
                "mask_b": ("MASK", {"tooltip": "The second mask. It is stretched to the size of mask A if needed."}),
                "operation": (list(OPS), {"default": "union", "tooltip": "union = A or B, intersect = A and B, subtract = A minus B, xor = in one only."}),
            }
        }

    def run(self, mask_a, mask_b, operation):
        if operation not in OPS:
            raise ValueError("unknown combine operation: %r (use %s)" % (operation, ", ".join(OPS)))
        return (mm.t_combine(mm.t_mask3(mask_a), mm.t_mask3(mask_b), operation),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskCombine", SYMaskCombine)
