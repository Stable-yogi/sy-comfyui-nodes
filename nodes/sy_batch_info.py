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


def size_warnings(width, height):
    """Pure function. Plain advice about the picture size, or an empty text when all is fine."""
    notes = []
    if width % 8 or height % 8:
        notes.append("size %dx%d is not a multiple of 8; many models need 8 (or 16/64)" % (width, height))
    mp = width * height / 1e6
    if mp > 4.2:
        notes.append("%.1f megapixels is large; it may run out of graphics memory" % mp)
    return "; ".join(notes)


def orientation(width, height):
    """Pure function. landscape, portrait or square."""
    return "square" if width == height else "landscape" if width > height else "portrait"


class SYBatchInfo:
    DESCRIPTION = ("Reports the number of pictures in a batch and their width, height and channels. The pictures pass through unchanged. "
                   "Also gives megapixels, landscape/portrait and a plain warning when the size is not a multiple of 8 or is very large.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "INT", "STRING", "FLOAT", "STRING", "STRING")
    RETURN_NAMES = ("images", "count", "width", "height", "channels", "text", "megapixels", "orientation", "warnings")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"images": ("IMAGE", {"tooltip": "The batch to measure. It is passed on unchanged."})}}

    def run(self, images):
        count, width, height, channels, text = describe_batch(images.shape)
        return (images, count, width, height, channels, text, round(width * height / 1e6, 3), orientation(width, height), size_warnings(width, height))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BatchInfo", SYBatchInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYBatchInfo"] = "Batch Info SY"
