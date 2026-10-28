"""Prompt Style Templates SY: 12 built-in style presets that add words before and after a prompt, plus a negative prompt."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

NONE = "none"
# name -> (positive prefix, positive suffix, negative text)
PRESETS = {
    "photo": ("photo of", "natural light, sharp focus, realistic skin texture, 35mm", "cartoon, painting, illustration, blurry, lowres"),
    "cinematic": ("cinematic still of", "dramatic lighting, shallow depth of field, film grain, anamorphic lens", "flat lighting, cartoon, lowres, oversaturated"),
    "portrait": ("studio portrait of", "soft key light, detailed eyes, 85mm lens, bokeh background", "deformed face, extra fingers, blurry, lowres"),
    "anime": ("anime illustration of", "clean line art, vibrant colors, detailed background", "photo, realistic, 3d render, lowres, bad anatomy"),
    "watercolor": ("watercolor painting of", "soft washes, paper texture, loose brush strokes", "photo, sharp edges, digital look, lowres"),
    "oil painting": ("oil painting of", "visible brush strokes, rich colors, canvas texture", "photo, flat colors, digital look, blurry"),
    "pixel art": ("pixel art of", "16-bit, limited palette, crisp pixels", "blurry, smooth gradients, photo, anti-aliasing"),
    "3d render": ("3d render of", "octane render, soft studio lighting, detailed materials", "painting, sketch, lowres, noisy"),
    "line art": ("black and white line art of", "clean ink lines, white background, high contrast", "color, shading, photo, blurry"),
    "fantasy": ("fantasy artwork of", "epic scene, magical atmosphere, intricate details, golden hour", "modern, photo, lowres, blurry"),
    "sci-fi": ("science fiction concept art of", "futuristic, neon accents, volumetric light, detailed machinery", "medieval, countryside, lowres, blurry"),
    "product shot": ("product photo of", "clean white background, soft shadows, studio lighting, high detail", "clutter, dirty, blurry, watermark, text"),
}
NAMES = [NONE] + list(PRESETS)


def apply_style(text, style, extra_negative=""):
    """Pure function. Returns (positive, negative)."""
    if not isinstance(text, str) or not isinstance(extra_negative, str):
        raise ValueError("text and extra_negative must be strings")
    if style not in NAMES:
        raise ValueError("unknown style %r: pick one of %s" % (style, ", ".join(NAMES)))
    if style == NONE:
        return (text.strip(), extra_negative.strip())
    prefix, suffix, negative = PRESETS[style]
    pos = ", ".join(p for p in (prefix, text.strip(), suffix) if p)
    neg = ", ".join(p for p in (negative, extra_negative.strip()) if p)
    return (pos, neg)


class SYPromptStyleTemplates:
    DESCRIPTION = "Pick one of 12 style presets (or none). Adds words before and after your prompt and gives a matching negative prompt."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "Your own prompt. The style words go around it."}),
                "style": (NAMES, {"default": "photo", "tooltip": "The style preset to use. 'none' leaves the prompt as it is."}),
            },
            "optional": {
                "extra_negative": ("STRING", {"multiline": True, "default": "", "tooltip": "Your own negative words, added after the preset negative."}),
            },
        }

    def run(self, text, style="photo", extra_negative=""):
        return apply_style(text, style, extra_negative)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptStyleTemplates", SYPromptStyleTemplates)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptStyleTemplates"] = "Prompt Style Templates SY"
