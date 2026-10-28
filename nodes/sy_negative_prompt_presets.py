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
}
PRESET_NAMES = tuple(PRESETS)
MODES = ("add after preset", "replace preset")


def negative_prompt(preset, custom="", mode="add after preset"):
    """Pure function. Returns the negative prompt text."""
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
    DESCRIPTION = "Gives a ready-made negative prompt for an image model. Add your own words after it, or replace it."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("negative_prompt",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (list(PRESET_NAMES), {"default": PRESET_NAMES[0], "tooltip": "Which ready-made negative prompt to use."}),
                "mode": (list(MODES), {"default": MODES[0], "tooltip": "Put your custom words after the preset, or use them instead."}),
            },
            "optional": {
                "custom": ("STRING", {"multiline": True, "default": "", "tooltip": "Your own words to avoid, separated by commas."}),
            },
        }

    def run(self, preset, mode, custom=""):
        return (negative_prompt(preset, custom, mode),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "NegativePromptPresets", SYNegativePromptPresets)
NODE_DISPLAY_NAME_MAPPINGS["SYNegativePromptPresets"] = "Negative Prompt Presets SY"
