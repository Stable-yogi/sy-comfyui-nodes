"""Megapixel Scale SY: new width and height for a target megapixel count, keeping the aspect."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SIDE = 65536


def scale_to_megapixels(width, height, megapixels, multiple):
    """Pure function. Returns (w, h) with area near `megapixels` million, aspect kept, both multiples of `multiple`."""
    width, height, multiple = int(width), int(height), int(multiple)
    megapixels = float(megapixels)
    if width < 1 or height < 1:
        raise ValueError("width and height must be at least 1, got %dx%d" % (width, height))
    if not (0 < megapixels <= 4096):  # also rejects nan
        raise ValueError("megapixels must be above 0 and at most 4096, got %s" % megapixels)
    if multiple < 1:
        raise ValueError("multiple must be at least 1, got %d" % multiple)
    area = megapixels * 1_000_000
    ratio = width / height
    w_ideal = math.sqrt(area * ratio)
    best = None
    for wc in (math.floor(w_ideal / multiple) * multiple, math.ceil(w_ideal / multiple) * multiple):
        wc = max(multiple, wc)
        h_ideal = wc / ratio
        for hc in (math.floor(h_ideal / multiple) * multiple, math.ceil(h_ideal / multiple) * multiple):
            hc = max(multiple, hc)
            score = abs(wc * hc - area) / area + abs(wc / hc - ratio) / ratio
            if best is None or score < best[0]:
                best = (score, wc, hc)
    w, h = int(best[1]), int(best[2])
    if w > MAX_SIDE or h > MAX_SIDE:
        raise ValueError("result %dx%d is too large, lower megapixels or use a less extreme shape" % (w, h))
    return (w, h)


class SYMegapixelScale:
    DESCRIPTION = ("Works out a new width and height that add up to a target number of megapixels. "
                   "The shape (aspect) stays the same. Both sides are rounded to a multiple.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Current width in pixels. Only its shape against the height matters."}),
                "height": ("INT", {"default": 1024, "min": 1, "max": MAX_SIDE, "tooltip": "Current height in pixels."}),
                "megapixels": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 4096.0, "step": 0.05, "tooltip": "Target size in millions of pixels. 1.0 is about 1024 by 1024."}),
                "multiple": ("INT", {"default": 16, "min": 1, "max": 256, "tooltip": "Width and height are rounded to a multiple of this. 16 suits most models."}),
            }
        }

    def run(self, width, height, megapixels, multiple):
        return scale_to_megapixels(width, height, megapixels, multiple)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MegapixelScale", SYMegapixelScale)
NODE_DISPLAY_NAME_MAPPINGS["SYMegapixelScale"] = "Megapixel Scale SY"
