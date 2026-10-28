"""Pixel Count Info SY: megapixels and a short text report for a width and height."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SIDE = 1_000_000


def pixel_info(width, height):
    """Pure function. Returns (megapixels, pixels, report_text)."""
    width, height = int(width), int(height)
    if width < 0 or height < 0:
        raise ValueError("width and height cannot be negative, got %dx%d" % (width, height))
    pixels = width * height
    mp = pixels / 1_000_000
    if width == 0 or height == 0:
        shape = "no shape (a side is 0)"
        orient = "empty"
    else:
        g = math.gcd(width, height)
        shape = "%d:%d (%.3f)" % (width // g, height // g, width / height)
        orient = "square" if width == height else ("landscape" if width > height else "portrait")
    text = "%dx%d, %d pixels, %.3f megapixels, aspect %s, %s" % (width, height, pixels, mp, shape, orient)
    return (mp, pixels, text)


class SYPixelCountInfo:
    DESCRIPTION = "Shows how big a picture size is: megapixels, total pixels and shape. Also gives a text line you can show or save."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "INT", "STRING")
    RETURN_NAMES = ("megapixels", "pixels", "report")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 0, "max": MAX_SIDE, "tooltip": "Width in pixels."}),
                "height": ("INT", {"default": 1024, "min": 0, "max": MAX_SIDE, "tooltip": "Height in pixels."}),
            }
        }

    def run(self, width, height):
        return pixel_info(width, height)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PixelCountInfo", SYPixelCountInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYPixelCountInfo"] = "Pixel Count Info SY"
