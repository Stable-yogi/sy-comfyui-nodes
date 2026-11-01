"""Video Size Fit SY: shrinks a size to fit a pixel budget, keeping the shape and a chosen multiple."""
import math

try:
    from ._sy_common import category, register
    from ._sy_b_sizeinfo import size_facts
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_b_sizeinfo import size_facts


def fit_size(width, height, max_megapixels, multiple_of=32, max_side=0):
    """Pure function. Returns (new_width, new_height). Never above the budget; never enlarges a size that already fits.
    max_side above 0 also keeps the longer side at or under that many pixels."""
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
    max_side = int(max_side)
    if max_side < 0:
        raise ValueError("max_side must be 0 (off) or more, got %d" % max_side)
    if max_side and max_side < m:
        raise ValueError("max_side %d is smaller than multiple_of %d. Raise max_side or lower multiple_of." % (max_side, m))
    scale = min(1.0, math.sqrt(budget / (width * height)))
    if max_side:
        scale = min(scale, max_side / float(max(width, height)))
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
    if max_side:
        while w > max_side:
            w -= m
        while h > max_side:
            h -= m
    return w, h


def fit_report(width, height, max_megapixels, multiple_of=32, max_side=0):
    """Pure function. Returns (w, h, info)."""
    w, h = fit_size(width, height, max_megapixels, multiple_of, max_side)
    width, height = int(width), int(height)
    if width * height <= float(max_megapixels) * 1000000.0 and (not max_side or max(width, height) <= max_side) and (w, h) == (width, height):
        return w, h, "%dx%d already fits (%s), kept" % (width, height, size_facts(w, h))
    return w, h, "%dx%d -> %dx%d (budget %g MP%s, %s)" % (width, height, w, h, float(max_megapixels), ", longest side max %d" % int(max_side) if max_side else "", size_facts(w, h))


class SYVideoSizeFit:
    DESCRIPTION = "Gives a new width and height with the same shape that stays inside a pixel budget and is a multiple of a number. An optional max_side also limits the longer side. The info line says what was done, or that the size already fits."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1280, "min": 1, "max": 16384, "tooltip": "Current width in pixels."}),
                "height": ("INT", {"default": 720, "min": 1, "max": 16384, "tooltip": "Current height in pixels."}),
                "max_pixels": ("FLOAT", {"default": 0.9, "min": 0.001, "max": 1000.0, "step": 0.01, "tooltip": "Pixel budget in megapixels. The result never goes above it."}),
                "multiple_of": ("INT", {"default": 32, "min": 1, "max": 256, "tooltip": "Width and height are rounded to a multiple of this number."}),
            },
            "optional": {
                "max_side": ("INT", {"default": 0, "min": 0, "max": 16384, "tooltip": "0 is off. Example: 1280 also keeps the longer side at or under 1280 pixels."}),
            },
        }

    def run(self, width, height, max_pixels, multiple_of, max_side=0):
        return fit_report(width, height, max_pixels, multiple_of, max_side)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VideoSizeFit", SYVideoSizeFit)
NODE_DISPLAY_NAME_MAPPINGS["SYVideoSizeFit"] = "Video Size Fit SY"
