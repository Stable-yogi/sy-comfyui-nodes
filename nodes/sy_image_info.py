"""Image Info SY: passes an image through and reports width, height, batch and megapixels."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def image_dims(shape):
    """Pure function. shape = (B, H, W, C) or (H, W, C) or (H, W). Returns (width, height, batch, megapixels)."""
    dims = tuple(int(x) for x in shape)
    if len(dims) == 4:
        batch, height, width = dims[0], dims[1], dims[2]
    elif len(dims) == 3:
        batch, height, width = 1, dims[0], dims[1]
    elif len(dims) == 2:
        batch, height, width = 1, dims[0], dims[1]
    else:
        raise ValueError("image shape must be [B,H,W,C], got %r" % (dims,))
    if min(batch, height, width) < 0:
        raise ValueError("image shape has a negative size: %r" % (dims,))
    return width, height, batch, (width * height) / 1000000.0


class SYImageInfo:
    DESCRIPTION = "Passes the image through and tells you its width, height, batch size and megapixels."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "FLOAT")
    RETURN_NAMES = ("image", "width", "height", "batch", "megapixels")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE", {"tooltip": "The picture to measure. It passes through unchanged."})}}

    def run(self, image):
        width, height, batch, mp = image_dims(tuple(image.shape))
        return (image, width, height, batch, mp)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageInfo", SYImageInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYImageInfo"] = "Image Info SY"
