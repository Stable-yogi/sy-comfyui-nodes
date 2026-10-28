"""Batch To List SY and List To Batch SY: switch between one batch tensor and a ComfyUI list of single pictures."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape, concat_tensors
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape, concat_tensors


def split_indices(total):
    """Pure function. One slot per picture: [0, 1, ... total-1]."""
    total = int(total)
    if total < 1:
        raise ValueError("batch is empty: need at least 1 picture, got %d" % total)
    return list(range(total))


def first_value(value, default=None):
    """Pure function. Nodes with INPUT_IS_LIST get every widget value wrapped in a list: take the first."""
    if isinstance(value, (list, tuple)):
        return value[0] if value else default
    return value


class SYBatchToList:
    DESCRIPTION = "Turns one batch into a list of single pictures, so the nodes after it run once per picture."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    OUTPUT_IS_LIST = (True,)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"images": ("IMAGE", {"tooltip": "The batch to split into single pictures."})}}

    def run(self, images):
        check_shape(images.shape)
        return ([images[i:i + 1] for i in split_indices(images.shape[0])],)


class SYListToBatch:
    DESCRIPTION = "Collects a list of pictures back into one batch. Pictures of other sizes can be resized to match the first."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("images", "count")
    INPUT_IS_LIST = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The list of pictures to collect into one batch."}),
            },
            "optional": {
                "resize_to_first": ("BOOLEAN", {"default": True, "tooltip": "On: resize every picture to the first one's size. Off: stop with an error when sizes differ."}),
            },
        }

    def run(self, images, resize_to_first=True):
        items = list(images) if isinstance(images, (list, tuple)) else [images]
        if not items:
            raise ValueError("the list is empty: connect at least one picture")
        out = concat_tensors(items, bool(first_value(resize_to_first, True)))
        return (out, int(out.shape[0]))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchToList", SYBatchToList)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ListToBatch", SYListToBatch)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchToList"] = "Batch To List SY"
NODE_DISPLAY_NAME_MAPPINGS["SYListToBatch"] = "List To Batch SY"
