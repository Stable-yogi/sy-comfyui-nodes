"""Negative Prompt Presets SY: ready-made negative prompts for image models, with a custom text to add or replace."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

PRESETS = {
    "general clean": "blurry, low quality, jpeg artifacts, watermark, text, logo, signature, cropped, out of frame",
    "photo realism": "cartoon, illustration, painting, drawing, plastic skin, oversaturated, overexposed, noise, grain, lowres",
    "portrait": "bad anatomy, deformed face, asymmetrical eyes, extra fingers, missing fingers, bad hands, blurry face, plastic skin",
    "full body": "bad anatomy, extra limbs, missing limbs, long neck, disfigured, bad proportions, bad hands, bad feet, cropped",
    "anime": "photo, realistic, 3d render, lowres, bad anatomy, bad hands, extra digits, jpeg artifacts, watermark, text",
    "landscape": "people, text, watermark, oversaturated, blurry, lowres, distorted horizon, noise, jpeg artifacts",
    "product shot": "dirty, scratches, fingerprints, harsh shadows, cluttered background, blurry, text, watermark, distorted shape",
    "architecture": "distorted lines, warped perspective, people, cars, text, watermark, blurry, lowres, cluttered",
    "painting": "photo, 3d render, digital noise, blurry, muddy colours, text, watermark, signature, lowres",
    "minimal": "blurry, lowres, watermark",
    "video": "flicker, jitter, morphing, warping, frozen frame, blurry, lowres, watermark, text, logo, distorted motion",
    "3d render": "photo, painting, flat shading, low poly, noisy textures, blurry, text, watermark, lowres, bad topology",
    "no text or logos": "text, letters, words, caption, subtitle, watermark, logo, signature, writing",
}
PRESET_NAMES = tuple(PRESETS)
MODES = ("add after preset", "replace preset")


def _split_terms(text):
    """Pure function. Splits on commas that are not inside brackets. Returns trimmed, non-empty terms."""
    terms, depth, cur = [], 0, []
    for ch in str(text):
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            terms.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    terms.append("".join(cur).strip())
    return [t for t in terms if t]


def negative_prompt(preset, custom="", mode="add after preset", remove_terms="", remove_duplicates=False, weight=0.0):
    """Pure function. Returns the negative prompt text.
    remove_terms: comma list of terms to take out (any case). remove_duplicates: keep the first of repeated terms.
    weight: 0 = off, otherwise the whole list is written as (terms:weight)."""
    if not isinstance(remove_terms, str):
        raise ValueError("remove_terms must be text, got %s" % type(remove_terms).__name__)
    weight = float(weight)
    if weight < 0 or weight > 2:
        raise ValueError("weight must be between 0 and 2, got %s" % weight)
    base = _basic_negative(preset, custom, mode)
    if not (remove_terms.strip() or remove_duplicates or weight):
        return base
    drop = {t.lower() for t in _split_terms(remove_terms)}
    seen, kept = set(), []
    for term in _split_terms(base):
        key = term.lower()
        if key in drop:
            continue
        if remove_duplicates:
            if key in seen:
                continue
            seen.add(key)
        kept.append(term)
    out = ", ".join(kept)
    if out and weight and weight != 1:
        out = "(%s:%g)" % (out, weight)
    return out


def negative_info(preset, mode, text):
    """Pure function. One plain line: where the text came from and how many terms it holds."""
    n = len(_split_terms(text))
    source = "your own words only" if mode == "replace preset" else "preset '%s'" % preset
    return "%d term%s from %s." % (n, "" if n == 1 else "s", source)


def _basic_negative(preset, custom="", mode="add after preset"):
    """Pure function. The preset text, with the custom text added after it or used instead."""
    if not isinstance(custom, str):
        raise ValueError("custom must be text, got %s" % type(custom).__name__)
    if mode not in MODES:
        raise ValueError("mode must be one of: %s (got %r)" % (", ".join(MODES), mode))
    if preset not in PRESETS:
        raise ValueError("unknown preset %r: pick one of %s" % (preset, ", ".join(PRESET_NAMES)))
    extra = custom.strip().strip(",").strip()
    if mode == "replace preset":
        if not extra:
            raise ValueError("mode is 'replace preset' but custom is empty: write your text or switch the mode")
        return extra
    if not extra:
        return PRESETS[preset]
    return PRESETS[preset] + ", " + extra


class SYNegativePromptPresets:
    DESCRIPTION = ("Gives a ready-made negative prompt for an image model. Add your own words after it, or replace it. "
                   "Can take out terms you do not want, drop repeats, and write the list with a weight. Also gives the term count.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("negative_prompt", "term_count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (list(PRESET_NAMES), {"default": PRESET_NAMES[0], "tooltip": "Which ready-made negative prompt to use."}),
                "mode": (list(MODES), {"default": MODES[0], "tooltip": "Put your custom words after the preset, or use them instead."}),
            },
            "optional": {
                "custom": ("STRING", {"multiline": True, "default": "", "tooltip": "Your own words to avoid, separated by commas."}),
                "remove_terms": ("STRING", {"default": "", "tooltip": "Terms to take out of the result, separated by commas. Any case."}),
                "remove_duplicates": ("BOOLEAN", {"default": False, "tooltip": "On: if a term appears twice, keep only the first."}),
                "weight": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 2.0, "step": 0.05, "tooltip": "0 = off. Otherwise the list is written as (terms:weight), for example 1.2."}),
            },
        }

    def run(self, preset, mode, custom="", remove_terms="", remove_duplicates=False, weight=0.0):
        out = negative_prompt(preset, custom, mode, remove_terms, remove_duplicates, weight)
        return out, len(_split_terms(out)), negative_info(preset, mode, out)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "NegativePromptPresets", SYNegativePromptPresets)
NODE_DISPLAY_NAME_MAPPINGS["SYNegativePromptPresets"] = "Negative Prompt Presets SY"
