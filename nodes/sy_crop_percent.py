"""Crop Percent SY: cuts a percentage off each edge of a picture."""
import math

try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image


def _px(size, percent):
    return int(math.floor(size * percent / 100.0 + 0.5))


def _snap_span(a, b, multiple, name):
    """Trim a start..end span to a multiple, taking half off each side."""
    size = b - a
    new = (size // multiple) * multiple
    if new < multiple:
        raise ValueError("the cropped %s is only %d pixels, less than one multiple of %d. Lower the crop or the multiple." % (name, size, multiple))
    a += (size - new) // 2
    return a, a + new


def crop_box(width, height, left, right, top, bottom, multiple=1):
    """Pure function. Returns (x0, y0, x1, y1) in pixels, end values not included.
    multiple above 1 trims the box a little more so width and height are multiples of it."""
    if width < 1 or height < 1:
        raise ValueError("picture size must be at least 1x1")
    for name, v in (("left", left), ("right", right), ("top", top), ("bottom", bottom)):
        if not 0.0 <= v <= 49.9:
            raise ValueError("%s must be between 0 and 49.9, got %s" % (name, v))
    x0 = _px(width, left)
    x1 = width - _px(width, right)
    y0 = _px(height, top)
    y1 = height - _px(height, bottom)
    if x1 <= x0:
        raise ValueError("left and right remove the whole width; lower left or right")
    if y1 <= y0:
        raise ValueError("top and bottom remove the whole height; lower top or bottom")
    multiple = int(multiple)
    if multiple < 1:
        raise ValueError("snap_multiple must be at least 1, got %d" % multiple)
    if multiple > 1:
        x0, x1 = _snap_span(x0, x1, multiple, "width")
        y0, y1 = _snap_span(y0, y1, multiple, "height")
    return (x0, y0, x1, y1)


def crop_info(width, height, box, multiple=1):
    """Pure function. One plain sentence about the crop."""
    x0, y0, x1, y1 = box
    if box == (0, 0, width, height):
        return "nothing cropped, the picture stays %dx%d" % (width, height)
    text = "cropped %dx%d -> %dx%d (removed left %d, right %d, top %d, bottom %d pixels)" % (
        width, height, x1 - x0, y1 - y0, x0, width - x1, y0, height - y1)
    if multiple > 1:
        text += ", trimmed to a multiple of %d" % multiple
    return text


class SYCropPercent:
    DESCRIPTION = "Cuts a percentage off each edge of a picture. Gives the cropped picture, its new size and an info line. The optional snap_multiple trims the result to a multiple of 8 or 64 so the next model node accepts it."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        def edge(side):
            return ("FLOAT", {"default": 0.0, "min": 0.0, "max": 49.9, "step": 0.1, "tooltip": "Percent of the %s to remove from this edge." % side})

        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to crop."}),
                "left": edge("width"),
                "right": edge("width"),
                "top": edge("height"),
                "bottom": edge("height"),
            },
            "optional": {
                "snap_multiple": ("INT", {"default": 1, "min": 1, "max": 256, "tooltip": "1 is off. 8 trims the result so width and height are multiples of 8 (many models need it)."}),
            },
        }

    def run(self, image, left, right, top, bottom, snap_multiple=1):
        need_image(image)
        _, h, w, _ = image.shape
        box = crop_box(w, h, left, right, top, bottom, snap_multiple)
        x0, y0, x1, y1 = box
        info = crop_info(w, h, box, int(snap_multiple))
        if box == (0, 0, w, h):
            return (image, w, h, info)
        return (image[:, y0:y1, x0:x1, :].contiguous(), x1 - x0, y1 - y0, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CropPercent", SYCropPercent)
NODE_DISPLAY_NAME_MAPPINGS["SYCropPercent"] = "Crop Percent SY"
