"""Resolution SY: width and height from a model preset, an aspect ratio and a megapixel target."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

# preset name -> (target megapixels, size multiple). "Custom" uses the node inputs.
PRESETS = {
    "Krea 2 (1 MP)": (1.0, 16),
    "Qwen Image 2.1 (1.5 MP)": (1.5, 16),
    "MOSS-Image (multiple of 32)": (1.0, 32),
    "Flux (1 MP)": (1.0, 16),
    "Custom": None,
}
ASPECTS = ("1:1", "4:3", "3:2", "16:9", "21:9", "3:4", "2:3", "9:16")
ORIENTATIONS = ("landscape", "portrait")
MULTIPLES = (8, 16, 32, 64)


def _ratio(aspect):
    """Landscape ratio (long side / short side) of an aspect text like '16:9'."""
    if aspect not in ASPECTS:
        raise ValueError("unknown aspect: %r" % (aspect,))
    a, b = (int(x) for x in aspect.split(":"))
    return max(a, b) / min(a, b)


def compute_size(model_preset, aspect, orientation, megapixels, multiple):
    """Pure function. Returns (width, height): area near the target, both multiples of `multiple`."""
    if model_preset not in PRESETS:
        raise ValueError("unknown model preset: %r" % (model_preset,))
    if orientation not in ORIENTATIONS:
        raise ValueError("unknown orientation: %r" % (orientation,))
    preset = PRESETS[model_preset]
    if preset is None:
        mp, mult = float(megapixels), int(multiple)
    else:
        mp, mult = preset
    if not mp > 0:
        raise ValueError("megapixels must be above 0")
    if mult < 1:
        raise ValueError("multiple must be at least 1")
    r = _ratio(aspect)  # width / height for landscape
    area = mp * 1_000_000
    w_ideal = math.sqrt(area * r)
    best = None
    for wc in (math.floor(w_ideal / mult) * mult, math.ceil(w_ideal / mult) * mult):
        wc = max(mult, wc)
        h_ideal = area / wc
        for hc in (math.floor(h_ideal / mult) * mult, math.ceil(h_ideal / mult) * mult):
            hc = max(mult, hc)
            score = abs(wc * hc - area) / area + abs(wc / hc - r) / r
            if best is None or score < best[0]:
                best = (score, wc, hc)
    w, h = best[1], best[2]
    if orientation == "portrait":
        w, h = h, w
    return (int(w), int(h))


class SYResolution:
    DESCRIPTION = ("Picks a width and height for a model. Choose a model preset and an aspect ratio. "
                   "Custom uses the megapixels and multiple you set.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_preset": (list(PRESETS), {"default": "Krea 2 (1 MP)", "tooltip": "Picks the size the chosen model works best at."}),
                "aspect": (list(ASPECTS), {"default": "1:1", "tooltip": "The shape of the picture. 1:1 is square, 16:9 is wide screen."}),
                "orientation": (list(ORIENTATIONS), {"default": "landscape", "tooltip": "Landscape is wider than tall. Portrait is taller than wide."}),
                "megapixels": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 16.0, "step": 0.05, "tooltip": "Picture size in millions of pixels. 1.0 is about 1024 by 1024."}),
                "multiple": ("INT", {"default": 16, "min": 8, "max": 64, "step": 8, "tooltip": "Width and height are rounded to a multiple of this. 16 suits most models."}),
            }
        }

    def run(self, model_preset, aspect, orientation, megapixels, multiple):
        return compute_size(model_preset, aspect, orientation, megapixels, multiple)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Resolution", SYResolution)
