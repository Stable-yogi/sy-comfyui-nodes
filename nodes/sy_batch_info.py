"""Batch Info SY: tells how many pictures a batch holds and how big they are."""
try:
    from ._sy_common import category, register
    from ._sy_batchtools import check_shape
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_batchtools import check_shape


def describe_batch(shape):
    """Pure function. Returns (count, width, height, channels, text) for a [count, height, width, channels] shape."""
    count, height, width, channels = check_shape(shape)
    word = "picture" if count == 1 else "pictures"
    text = "%d %s, %dx%d, %d channels" % (count, word, width, height, channels)
    return count, width, height, channels, text


class SYBatchInfo:
    DESCRIPTION = "Reports the number of pictures in a batch and their width, height and channels. The pictures pass through unchanged."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("images", "count", "width", "height", "channels", "text")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"images": ("IMAGE", {"tooltip": "The batch to measure. It is passed on unchanged."})}}

    def run(self, images):
        count, width, height, channels, text = describe_batch(images.shape)
        return (images, count, width, height, channels, text)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchInfo", SYBatchInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchInfo"] = "Batch Info SY"
