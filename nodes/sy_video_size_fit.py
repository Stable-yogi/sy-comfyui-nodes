"""Video Size Fit SY: shrinks a size to fit a pixel budget, keeping the shape and a chosen multiple."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def fit_size(width, height, max_megapixels, multiple_of=32):
    """Pure function. Returns (new_width, new_height). Never above the budget; never enlarges a size that already fits."""
    width = int(width)
    height = int(height)
    m = int(multiple_of)
    budget = float(max_megapixels) * 1000000.0
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1, got %dx%d" % (width, height))
    if m < 1:
        raise ValueError("multiple_of must be at least 1, got %d" % m)
    if not budget > 0:
        raise ValueError("max_pixels must be greater than 0, got %s" % max_megapixels)
    if m * m > budget:
        raise ValueError("max_pixels is too small: even %dx%d is over the budget" % (m, m))
    scale = min(1.0, math.sqrt(budget / (width * height)))
    w = max(m, int(round(width * scale / m)) * m)
    h = max(m, int(round(height * scale / m)) * m)
    while w * h > budget:
        # lower the side that sits furthest above its ideal size
        rw = w / (width * scale)
        rh = h / (height * scale)
        if (rw >= rh and w > m) or h <= m:
            w -= m
        else:
            h -= m
    return w, h


class SYVideoSizeFit:
    DESCRIPTION = "Gives a new width and height with the same shape that stays inside a pixel budget and is a multiple of a number."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1280, "min": 1, "max": 16384, "tooltip": "Current width in pixels."}),
                "height": ("INT", {"default": 720, "min": 1, "max": 16384, "tooltip": "Current height in pixels."}),
                "max_pixels": ("FLOAT", {"default": 0.9, "min": 0.001, "max": 1000.0, "step": 0.01, "tooltip": "Pixel budget in megapixels. The result never goes above it."}),
                "multiple_of": ("INT", {"default": 32, "min": 1, "max": 256, "tooltip": "Width and height are rounded to a multiple of this number."}),
            }
        }

    def run(self, width, height, max_pixels, multiple_of):
        return fit_size(width, height, max_pixels, multiple_of)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoSizeFit", SYVideoSizeFit)
NODE_DISPLAY_NAME_MAPPINGS["SYVideoSizeFit"] = "Video Size Fit SY"
