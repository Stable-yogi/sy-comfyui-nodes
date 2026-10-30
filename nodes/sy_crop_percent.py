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


def crop_box(width, height, left, right, top, bottom):
    """Pure function. Returns (x0, y0, x1, y1) in pixels, end values not included."""
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
    return (x0, y0, x1, y1)


class SYCropPercent:
    DESCRIPTION = "Cuts a percentage off each edge of a picture. Gives the cropped picture and its new size."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")

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
            }
        }

    def run(self, image, left, right, top, bottom):
        need_image(image)
        _, h, w, _ = image.shape
        x0, y0, x1, y1 = crop_box(w, h, left, right, top, bottom)
        if (x0, y0, x1, y1) == (0, 0, w, h):
            return (image, w, h)
        return (image[:, y0:y1, x0:x1, :].contiguous(), x1 - x0, y1 - y0)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CropPercent", SYCropPercent)
NODE_DISPLAY_NAME_MAPPINGS["SYCropPercent"] = "Crop Percent SY"
