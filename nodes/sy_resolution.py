"""Resolution SY: width and height from a model preset, an aspect ratio and a megapixel target."""
import math

try:
    from ._sy_common import category, register
    from ._sy_b_sizeinfo import size_facts
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_b_sizeinfo import size_facts

# preset name -> (target megapixels, size multiple). "Custom" uses the node inputs.
PRESETS = {
    "Krea 2 (1 MP)": (1.0, 16),
    "Qwen Image 2.1 (1.5 MP)": (1.5, 16),
    "MOSS-Image (multiple of 32)": (1.0, 32),
    "Flux (1 MP)": (1.0, 16),
    "Custom": None,
    "SDXL (1 MP, multiple of 64)": (1.0, 64),
    "SD 1.5 (0.26 MP, multiple of 64)": (0.26, 64),
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


def _square(area, mult):
    """Pure function. Exact square side for an area: nearest multiple of `mult`; when that misses the target by more than
    1.5 percent, a multiple of 64 (such as 1024) is used if it is within 5 percent and also a multiple of `mult`."""
    ideal = math.sqrt(area)
    cands = [max(mult, math.floor(ideal / mult) * mult), max(mult, math.ceil(ideal / mult) * mult)]
    side = min(cands, key=lambda c: (abs(c * c - area), -c))
    if abs(side * side - area) / area > 0.015:
        nice = max(64, int(round(ideal / 64.0)) * 64)
        if nice % mult == 0 and abs(nice * nice - area) / area <= 0.05:
            side = nice
    return side, side


def compute_size(model_preset, aspect, orientation, megapixels, multiple, max_megapixels=0.0):
    """Pure function. Returns (width, height): area near the target, both multiples of `multiple`.
    max_megapixels above 0 is a memory-safety cap: the target is lowered until the result fits under it."""
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
    cap = float(max_megapixels)
    if not cap >= 0:
        raise ValueError("max_megapixels must be 0 (off) or more, got %s" % cap)
    r = _ratio(aspect)  # width / height for landscape

    def best_for(mpx):
        area = mpx * 1_000_000
        if r == 1.0:
            return _square(area, mult)
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
        return best[1], best[2]

    w, h = best_for(mp)
    if cap > 0:
        if mult * mult > cap * 1_000_000:
            raise ValueError("max_megapixels %g is too small: even %dx%d is over it. Raise it or lower multiple." % (cap, mult, mult))
        tries = 0
        while w * h > cap * 1_000_000 and tries < 200 and (w > mult or h > mult):
            mp *= 0.97
            w, h = best_for(mp)
            tries += 1
    if orientation == "portrait":
        w, h = h, w
    return (int(w), int(h))


def resolution_report(model_preset, aspect, orientation, megapixels, multiple, max_megapixels=0.0):
    """Pure function. Returns (width, height, info)."""
    w, h = compute_size(model_preset, aspect, orientation, megapixels, multiple, max_megapixels)
    info = "%s, %s %s: %dx%d (%s)" % (model_preset, aspect, orientation, w, h, size_facts(w, h))
    if float(max_megapixels) > 0 and (w, h) != compute_size(model_preset, aspect, orientation, megapixels, multiple):
        info += ", lowered to stay under %g MP" % float(max_megapixels)
    return w, h, info


class SYResolution:
    DESCRIPTION = "Picks a width and height for a model. Choose a model preset and an aspect ratio. Custom uses the megapixels and multiple you set. Optional max_megapixels keeps the size small enough for your card, and the info line shows the final size, shape and multiple."
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_preset": (list(PRESETS), {"default": "Krea 2 (1 MP)", "tooltip": "Picks the size the chosen model works best at."}),
                "aspect": (list(ASPECTS), {"default": "1:1", "tooltip": "The shape of the picture. 1:1 is square, 16:9 is wide screen."}),
                "orientation": (list(ORIENTATIONS), {"default": "landscape", "tooltip": "Landscape is wider than tall. Portrait is taller than wide."}),
                "megapixels": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 16.0, "step": 0.05, "tooltip": "Picture size in millions of pixels. 1.0 is about 1024 by 1024."}),
                "multiple": ("INT", {"default": 16, "min": 8, "max": 64, "step": 8, "tooltip": "Width and height are rounded to a multiple of this. 16 suits most models."}),
            },
            "optional": {
                "max_megapixels": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 64.0, "step": 0.1, "tooltip": "0 is off. Example: 1.5 lowers the size so it never goes over 1.5 million pixels."}),
            },
        }

    def run(self, model_preset, aspect, orientation, megapixels, multiple, max_megapixels=0.0):
        return resolution_report(model_preset, aspect, orientation, megapixels, multiple, max_megapixels)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Resolution", SYResolution)
