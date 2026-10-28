"""Prompt Sections SY: joins named prompt parts (subject, setting, lighting...) into one prompt."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
SECTIONS = ("subject", "setting", "lighting", "camera", "style", "extra")
LABEL_MODES = ("none", "label_colon")


def build_sections(parts, join_with=", ", label_mode="none"):
    """Pure function. parts is a dict name -> text. Returns (text, used_count)."""
    if label_mode not in LABEL_MODES:
        raise ValueError("unknown label_mode %r: choose one of %s" % (label_mode, ", ".join(LABEL_MODES)))
    join_with = ", " if join_with is None else str(join_with)
    used = []
    total = 0
    for name in SECTIONS:
        value = parts.get(name)
        value = "" if value is None else str(value).strip()
        total += len(value)
        if value == "":
            continue
        used.append(("%s: %s" % (name.capitalize(), value)) if label_mode == "label_colon" else value)
    if total > MAX_INPUT:
        raise ValueError("sections are too long: %d characters (limit %d)" % (total, MAX_INPUT))
    return join_with.join(used), len(used)


class SYPromptSections:
    DESCRIPTION = "Joins prompt parts (subject, setting, lighting, camera, style, extra) into one prompt. Empty parts are skipped."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "sections_used")

    @classmethod
    def INPUT_TYPES(cls):
        def box(tip):
            return ("STRING", {"default": "", "multiline": True, "tooltip": tip})
        return {
            "required": {
                "join_with": ("STRING", {"default": ", ", "tooltip": "The text put between the parts. Use a comma, or a new line."}),
                "label_mode": (list(LABEL_MODES), {"default": "none", "tooltip": "label_colon puts a name before each part, like 'Lighting: soft'."}),
            },
            "optional": {
                "subject": box("Who or what the picture shows."),
                "setting": box("Where it happens: place, time, weather."),
                "lighting": box("The light: soft, golden hour, neon and so on."),
                "camera": box("Camera, lens and angle."),
                "style": box("The look: painting, photo, anime and so on."),
                "extra": box("Anything else you want to add at the end."),
            },
        }

    def run(self, join_with=", ", label_mode="none", subject="", setting="", lighting="", camera="", style="", extra=""):
        parts = {"subject": subject, "setting": setting, "lighting": lighting,
                 "camera": camera, "style": style, "extra": extra}
        return build_sections(parts, join_with, label_mode)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptSections", SYPromptSections)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptSections"] = "Prompt Sections SY"
