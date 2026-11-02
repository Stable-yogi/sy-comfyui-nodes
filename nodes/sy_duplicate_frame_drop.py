"""Duplicate Frame Drop SY: drops frames that did not change from the frame before."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def check_tolerance(tolerance):
    """Pure function. Raises ValueError with a plain message for a bad tolerance."""
    if not 0.0 <= float(tolerance) <= 0.2:
        raise ValueError("tolerance must be between 0 and 0.2, got %s" % tolerance)


def pick_kept(diffs, tolerance, keep_first=True):
    """Pure function. diffs[i] = mean change of frame i from frame i-1 (diffs[0] is ignored).

    A frame is kept when it changed by more than the tolerance. Frame 0 is kept when keep_first is on.
    At least one frame always stays.
    """
    check_tolerance(tolerance)
    if len(diffs) == 0:
        raise ValueError("there are no frames to check")
    kept = []
    for i, d in enumerate(diffs):
        if i == 0:
            if keep_first:
                kept.append(0)
        elif d > tolerance:
            kept.append(i)
    if not kept:
        kept = [0]
    return kept


def format_indices(ids):
    """Pure function. '0,1,4' text."""
    return ",".join(str(i) for i in ids)


def frame_diffs(images):
    """Torch function. Mean absolute change of each frame from the one before (first entry is 0)."""
    n = images.shape[0]
    diffs = [0.0]
    for i in range(1, n):
        diffs.append(float((images[i].float() - images[i - 1].float()).abs().mean().item()))
    return diffs


class SYDuplicateFrameDrop:
    DESCRIPTION = ("Drops frames that did not change from the frame before. Tells you which frames stayed and how many "
                   "were dropped. At least one frame always stays.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "STRING", "INT")
    RETURN_NAMES = ("images", "kept_indices", "dropped")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The frames of the clip, in order."}),
                "tolerance": ("FLOAT", {"default": 0.004, "min": 0.0, "max": 0.2, "step": 0.001, "tooltip": "A frame changing by no more than this (average per pixel, 0 to 1) counts as a copy."}),
                "keep_first": ("BOOLEAN", {"default": True, "tooltip": "On: always keep the first frame. Off: the first frame can be dropped too."}),
            }
        }

    def run(self, images, tolerance, keep_first):
        ids = pick_kept(frame_diffs(images), tolerance, keep_first)
        return (images[ids], format_indices(ids), int(images.shape[0] - len(ids)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DuplicateFrameDrop", SYDuplicateFrameDrop)
NODE_DISPLAY_NAME_MAPPINGS["SYDuplicateFrameDrop"] = "Duplicate Frame Drop SY"
