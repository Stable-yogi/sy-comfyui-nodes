"""Prompt Sections SY: joins named prompt parts (subject, setting, lighting...) into one prompt."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
SECTIONS = ("subject", "setting", "lighting", "camera", "style", "extra")
LABEL_MODES = ("none", "label_colon")


def _drop_repeat_tags(used):
    """Removes a comma tag that already appeared in an earlier part (case ignored). Returns the new parts."""
    seen = set()
    out = []
    for value in used:
        keep = []
        for tag in value.split(","):
            tag = tag.strip()
            if not tag or tag.lower() in seen:
                continue
            seen.add(tag.lower())
            keep.append(tag)
        if keep:
            out.append(", ".join(keep))
    return out


def build_sections(parts, join_with=", ", label_mode="none", remove_repeats=False):
    """Pure function. parts is a dict name -> text. Returns (text, used_count).
    remove_repeats drops a tag that is already in an earlier part (parts are split at commas). Not used with label_colon."""
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
    if remove_repeats and label_mode == "none":
        used = _drop_repeat_tags(used)
    return join_with.join(used), len(used)


def sections_info(parts, text):
    """Pure function. One plain line: which parts were used, which were empty, the size."""
    names = [n for n in SECTIONS if str(parts.get(n) or "").strip()]
    if not names:
        return "All parts are empty, so the prompt is empty"
    empty = [n for n in SECTIONS if n not in names]
    line = "Used %d of %d parts (%s)" % (len(names), len(SECTIONS), ", ".join(names))
    if empty:
        line += "; empty: " + ", ".join(empty)
    return line + "; %d characters, about %d tokens" % (len(text), -(-len(text) // 4))


class SYPromptSections:
    DESCRIPTION = ("Joins prompt parts (subject, setting, lighting, camera, style, extra) into one prompt. Empty parts are skipped, "
                   "repeated tags can be removed, and the info line shows which parts were used and the size.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("text", "sections_used", "info")

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
                "remove_repeats": ("BOOLEAN", {"default": False, "tooltip": "On: a comma tag already used in an earlier part is dropped. Not with label_colon."}),
            },
        }

    def run(self, join_with=", ", label_mode="none", subject="", setting="", lighting="", camera="", style="", extra="",
            remove_repeats=False):
        parts = {"subject": subject, "setting": setting, "lighting": lighting,
                 "camera": camera, "style": style, "extra": extra}
        text, used = build_sections(parts, join_with, label_mode, remove_repeats)
        return (text, used, sections_info(parts, text))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptSections", SYPromptSections)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptSections"] = "Prompt Sections SY"
