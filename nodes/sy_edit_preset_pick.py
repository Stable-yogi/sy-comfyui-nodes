"""Edit Preset Pick SY: picks ready-made wording for common picture edits, or uses your own text instead."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

PRESETS = {
    "remove_object": "Remove the unwanted object from the picture and fill the gap so it looks natural.",
    "fix_lighting": "Fix the lighting so the scene is evenly lit, with soft natural light and no harsh shadows.",
    "colourise_black_and_white": "Turn this black and white picture into a natural full-colour picture.",
    "make_it_daytime": "Change the scene so it is bright daytime with a clear sky and natural sunlight.",
    "make_it_night": "Change the scene so it is night time, dark and lit by moonlight and soft lamps.",
    "remove_background_to_white": "Remove the background and put the subject on a plain white background.",
    "sharpen_and_clean": "Make the picture sharper and cleaner by removing blur, noise and small marks.",
    "change_season_to_winter": "Change the season to winter with snow on the ground and bare, frosty trees.",
    "remove_text_and_watermark": "Remove all text, logos and watermarks from the picture and rebuild the area behind them naturally.",
    "blur_background": "Blur the background softly like a portrait lens, and keep the subject sharp.",
    "golden_hour_light": "Change the light to warm golden hour sunlight with long soft shadows.",
    "turn_to_black_and_white": "Turn this picture into a classic black and white photo with rich contrast.",
}


def pick_preset(preset, custom_override=""):
    """Pure function. A non-empty custom_override wins over the preset."""
    custom = str(custom_override or "").strip()
    if custom:
        return custom
    if preset not in PRESETS:
        raise ValueError("unknown preset %r: choose one of %s" % (preset, ", ".join(PRESETS)))
    return PRESETS[preset]


def pick_with_info(preset, custom_override="", extra=""):
    """Pure function. Returns (text, info). extra is added as a closing sentence to whichever text is used."""
    custom = str(custom_override or "").strip()
    text = pick_preset(preset, custom)
    tail = " ".join(str(extra or "").split())
    if tail:
        text = text.rstrip() + " " + (tail if tail.endswith((".", "!", "?")) else tail + ".")
    if custom:
        info = "Used your own text (preset %s ignored)." % preset
    else:
        info = "Used preset %s." % preset
    if tail:
        info += " Added your extra sentence."
    return text, info


class SYEditPresetPick:
    DESCRIPTION = ("Gives ready-made wording for common picture edits like fixing light, blurring or removing the background. Your own "
                   "text replaces it if you type any, and an extra sentence can be added to either. An info line says which was used.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (list(PRESETS), {"default": "remove_object", "tooltip": "The ready-made edit wording to use."}),
            },
            "optional": {
                "custom_override": ("STRING", {"default": "", "multiline": True, "tooltip": "If you type anything here, it is used instead of the preset."}),
                "extra": ("STRING", {"default": "", "tooltip": "A closing sentence added to the text, for example: Keep the dog unchanged."}),
            },
        }

    def run(self, preset, custom_override="", extra=""):
        return pick_with_info(preset, custom_override, extra)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EditPresetPick", SYEditPresetPick)
