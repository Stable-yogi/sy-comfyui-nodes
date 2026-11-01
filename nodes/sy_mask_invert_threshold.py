"""Mask Invert Threshold SY: flips a mask and/or makes it hard black and white."""
try:
    from ._sy_common import category, register
    from . import _sy_mask_math as mm
    from ._sy_d3_info import pct_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    import _sy_mask_math as mm
    from _sy_d3_info import pct_text


def invert_info(invert, use_threshold, threshold, white, total):
    """Pure function. Plain sentence: which steps ran and how much of the mask is white afterwards (white = pixel count)."""
    if not invert and not use_threshold:
        steps = "Both switches are off, so the mask was passed through unchanged"
    else:
        done = []
        if use_threshold:
            done.append("cut at %.2f (at or above is white)" % threshold)
        if invert:
            done.append("flipped")
        steps = "The mask was " + " then ".join(done)
    text = "%s: %s of it is white now." % (steps, pct_text(white, total))
    if white == 0:
        text += " It is all black."
    elif white == total:
        text += " It is all white."
    return text


def invert_threshold(rows, invert, use_threshold, threshold):
    """Pure function on a nested-list mask [H][W]. Threshold is applied first, then the flip."""
    if threshold < 0.0 or threshold > 1.0:
        raise ValueError("threshold must be between 0 and 1")
    return mm.threshold_invert_list(rows, bool(invert), bool(use_threshold), float(threshold))


class SYMaskInvertThreshold:
    DESCRIPTION = "Flips a mask (white and black swap) and can first turn it into hard black and white at a cut-off value. The info output says what was done and how much is white, and warns about an all-black or all-white result."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("MASK", "STRING")
    RETURN_NAMES = ("mask", "info")

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
        if m.shape[0] < 1:
            raise ValueError("the mask batch is empty: connect at least 1 mask")
        if use_threshold:
            m = (m >= threshold).float()
        if invert:
            m = 1.0 - m
        white = int((m >= 0.5).sum())
        return (m, invert_info(invert, use_threshold, float(threshold), white, int(m.numel())))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MaskInvertThreshold", SYMaskInvertThreshold)
