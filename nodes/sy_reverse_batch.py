"""Reverse Batch SY: plays a batch of pictures backwards."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape


def reverse_indices(total):
    """Pure function. Indices total-1 down to 0."""
    total = int(total)
    if total < 1:
        raise ValueError("batch is empty: need at least 1 picture, got %d" % total)
    return list(range(total - 1, -1, -1))


class SYReverseBatch:
    DESCRIPTION = "Turns a batch of pictures around so the last one comes first. Handy for playing a video backwards."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"images": ("IMAGE", {"tooltip": "The batch of pictures or video frames to reverse."})}}

    def run(self, images):
        check_shape(images.shape)
        return (images[reverse_indices(images.shape[0])],)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ReverseBatch", SYReverseBatch)
NODE_DISPLAY_NAME_MAPPINGS["SYReverseBatch"] = "Reverse Batch SY"
