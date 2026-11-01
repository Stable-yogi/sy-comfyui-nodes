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


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def aspect_text(width, height):
    """Pure function. Shape of the picture as a simple ratio and a decimal, for example '4:3 (1.333)'."""
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1 to work out the shape, got %dx%d" % (width, height))
    g = gcd(width, height)
    rw, rh = width // g, height // g
    dec = width / float(height)
    if rw > 50 or rh > 50:  # an odd size: look for a well-known ratio that is very close
        for a, b in ((1, 1), (5, 4), (4, 3), (3, 2), (16, 10), (16, 9), (21, 9), (2, 1), (3, 1)):
            for x, y in ((a, b), (b, a)):
                if abs(dec - x / float(y)) / (x / float(y)) < 0.01:
                    return "about %d:%d (%.3f)" % (x, y, dec)
        return "%.3f" % dec
    return "%d:%d (%.3f)" % (rw, rh, dec)


def size_notes(width, height, batch, megapixels):
    """Pure function. Plain warnings about sizes that models dislike."""
    notes = []
    if width % 8 or height % 8:
        notes.append("width or height is not a multiple of 8, which most models need")
    elif width % 64 or height % 64:
        notes.append("not a multiple of 64 (fine for most models, some prefer it)")
    if megapixels > 4.5:
        notes.append("%.1f megapixels is large: it may run out of graphics memory" % megapixels)
    if batch > 1 and (batch - 1) % 4 == 0:
        notes.append("batch of %d fits video models that need 4n+1 frames" % batch)
    return notes


def info_text(width, height, batch, megapixels, channels):
    """Pure function. One plain line about the picture."""
    kind = {1: "grey", 3: "RGB", 4: "RGB with transparency"}.get(int(channels), "%d channels" % channels)
    text = "%dx%d, shape %s, %.2f megapixels, %d picture(s), %s" % (width, height, aspect_text(width, height), megapixels, batch, kind)
    notes = size_notes(width, height, batch, megapixels)
    return text + ("; " + "; ".join(notes) if notes else "") + "."


class SYImageInfo:
    DESCRIPTION = ("Passes the image through and tells you its width, height, batch size and megapixels. Also gives the shape "
                   "(4:3, 16:9 ...), the colour channels, and an info line that warns about sizes most models dislike.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT", "FLOAT", "INT", "STRING", "STRING")
    RETURN_NAMES = ("image", "width", "height", "batch", "megapixels", "channels", "aspect", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"image": ("IMAGE", {"tooltip": "The picture to measure. It passes through unchanged."})}}

    def run(self, image):
        shape = tuple(image.shape)
        width, height, batch, mp = image_dims(shape)
        channels = int(shape[3]) if len(shape) == 4 else int(shape[2]) if len(shape) == 3 else 1
        if width < 1 or height < 1:
            raise ValueError("the picture has no pixels (%dx%d): check the node that makes it" % (width, height))
        return (image, width, height, batch, mp, channels, aspect_text(width, height), info_text(width, height, batch, mp, channels))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ImageInfo", SYImageInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYImageInfo"] = "Image Info SY"
