"""Batch Concat SY: joins two to four picture batches into one batch."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import concat_plan, concat_tensors
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import concat_plan, concat_tensors


def concat_info(counts, width, height, resized):
    """Pure function. One plain sentence about a join. counts is the picture count of each part."""
    if not counts:
        raise ValueError("nothing to join: connect at least two batches")
    total = sum(counts)
    parts = "+".join(str(c) for c in counts)
    note = ", other sizes were resized to match the first" if resized else ""
    return "Joined %d batches (%s = %d pictures) at %dx%d%s" % (len(counts), parts, total, width, height, note)


class SYBatchConcat:
    DESCRIPTION = ("Joins two to four picture batches into one batch, in order. Other sizes can be resized to match the first. "
                   "Also tells you how many pictures each part gave and the final size.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "STRING")
    RETURN_NAMES = ("images", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_1": ("IMAGE", {"tooltip": "First batch. Its size and channels set the size of the result."}),
                "image_2": ("IMAGE", {"tooltip": "Second batch, added after the first."}),
                "resize_to_first": ("BOOLEAN", {"default": True, "tooltip": "On: resize other batches to the first one's size. Off: stop with an error when sizes differ."}),
            },
            "optional": {
                "image_3": ("IMAGE", {"tooltip": "Optional third batch."}),
                "image_4": ("IMAGE", {"tooltip": "Optional fourth batch."}),
            },
        }

    def run(self, image_1, image_2, resize_to_first, image_3=None, image_4=None):
        parts = [t for t in (image_1, image_2, image_3, image_4) if t is not None]
        out = concat_tensors(parts, bool(resize_to_first))
        sizes = set((int(t.shape[2]), int(t.shape[1])) for t in parts)
        info = concat_info([int(t.shape[0]) for t in parts], int(out.shape[2]), int(out.shape[1]), len(sizes) > 1)
        return (out, int(out.shape[0]), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchConcat", SYBatchConcat)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchConcat"] = "Batch Concat SY"
