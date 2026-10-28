"""Aspect From Size SY: turns a width and height into a ratio text like 16:9 and a float ratio."""
import math

try:
    from ._sy_common import category, display_name
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, display_name

COMMON = ("1:1", "5:4", "4:3", "3:2", "16:9", "2:1", "21:9",
          "4:5", "3:4", "2:3", "9:16", "1:2", "9:21")
SMALL = 24  # an exact ratio is kept when both terms are at most this


def aspect_from_size(width, height):
    """Pure function. Returns (ratio text, float ratio = width / height)."""
    width, height = int(width), int(height)
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1")
    g = math.gcd(width, height)
    a, b = width // g, height // g
    value = width / height
    if max(a, b) <= SMALL:
        return ("%d:%d" % (a, b), value)
    best = min(COMMON, key=lambda t: abs(math.log(value / (int(t.split(":")[0]) / int(t.split(":")[1])))))
    return (best, value)


class SYAspectFromSize:
    DESCRIPTION = ("Reads a width and height and gives the ratio as text, like 16:9, plus the ratio as a number. "
                   "An odd ratio is matched to the nearest common one.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "FLOAT")
    RETURN_NAMES = ("ratio", "ratio_float")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 1, "max": 65536, "tooltip": "Picture width in pixels. Used with height to find the shape, like 16:9."}),
                "height": ("INT", {"default": 1024, "min": 1, "max": 65536, "tooltip": "Picture height in pixels. Used with width to find the shape, like 16:9."}),
            }
        }

    def run(self, width, height):
        return aspect_from_size(width, height)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_CLASS_MAPPINGS["SYAspectFromSize"] = SYAspectFromSize
NODE_DISPLAY_NAME_MAPPINGS["SYAspectFromSize"] = display_name("Aspect From Size")
