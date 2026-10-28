"""Mask Invert Threshold SY: flips a mask and/or makes it hard black and white."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm


def invert_threshold(rows, invert, use_threshold, threshold):
    """Pure function on a nested-list mask [H][W]. Threshold is applied first, then the flip."""
    if threshold < 0.0 or threshold > 1.0:
        raise ValueError("threshold must be between 0 and 1")
    return mm.threshold_invert_list(rows, bool(invert), bool(use_threshold), float(threshold))


class SYMaskInvertThreshold:
    DESCRIPTION = "Flips a mask (white and black swap) and can first turn it into hard black and white at a cut-off value."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", {"tooltip": "The mask to change."}),
                "invert": ("BOOLEAN", {"default": True, "tooltip": "Swap white and black."}),
                "use_threshold": ("BOOLEAN", {"default": False, "tooltip": "Turn soft grays into pure black or white first."}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Values at or above this become white. Only used when use_threshold is on."}),
            }
        }

    def run(self, mask, invert, use_threshold, threshold):
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("threshold must be between 0 and 1")
        m = mm.t_mask3(mask)
        if use_threshold:
            m = (m >= threshold).float()
        if invert:
            m = 1.0 - m
        return (m,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskInvertThreshold", SYMaskInvertThreshold)
