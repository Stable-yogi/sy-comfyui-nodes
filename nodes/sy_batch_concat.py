"""Batch Concat SY: joins two to four picture batches into one batch."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import concat_plan, concat_tensors
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import concat_plan, concat_tensors


class SYBatchConcat:
    DESCRIPTION = "Joins two to four picture batches into one batch, in order. Other sizes can be resized to match the first."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "count")

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
        return (out, int(out.shape[0]))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchConcat", SYBatchConcat)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchConcat"] = "Batch Concat SY"
