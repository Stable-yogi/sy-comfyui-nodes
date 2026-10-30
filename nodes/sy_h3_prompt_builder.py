"""H3 Prompt Builder SY: builds one tidy prompt for a video model from style, world, action and dialogue."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_TIME_RE = re.compile(r"^\d+(\.\d+)?s?\s*-\s*\d+(\.\d+)?s?\s*:\s*\S.*$")
_PIC_RE = re.compile(r"picture\s*(\d)", re.IGNORECASE)
MAX_CHARS = 4000


def _lines(text):
    return [l.strip() for l in str(text or "").splitlines() if l.strip()]


def build_prompt(style, world, action, dialogue="", dialogue_language="", picture_count=0, time_codes=""):
    """Pure function. Returns (prompt, notes)."""
    style = str(style or "").strip()
    world = str(world or "").strip()
    action = str(action or "").strip()
    lang = str(dialogue_language or "").strip()
    d_lines = _lines(dialogue)
    t_lines = _lines(time_codes)
    if not (style or world or action or d_lines):
        raise ValueError("write at least one of style, world, action, dialogue")
    picture_count = int(picture_count)

    blocks = []
    if style:
        blocks.append("Style: " + style)
    if world:
        blocks.append("World: " + world)
    if action:
        blocks.append("Action: " + action)
    if t_lines:
        blocks.append("Timeline:\n" + "\n".join(t_lines))
    if d_lines:
        if lang:
            blocks.append("\n".join("<d>[%s] %s</d>" % (lang, l) for l in d_lines))
        else:
            blocks.append("\n".join("<d>%s</d>" % l for l in d_lines))
    prompt = "\n\n".join(blocks)

    notes = []
    for label, text in (("world", world), ("action", action), ("time_codes", "\n".join(t_lines))):
        seen = set()
        for mt in _PIC_RE.finditer(text):
            num = int(mt.group(1))
            if num > picture_count and num not in seen:
                seen.add(num)
                notes.append("%s mentions Picture %d but picture_count is %d" % (label, num, picture_count))
    for i, l in enumerate(t_lines, 1):
        if not _TIME_RE.match(l):
            notes.append("time code line %d is not like 0-4s: text" % i)
    if len(prompt) > MAX_CHARS:
        notes.append("prompt has %d characters; more than %d may be cut off" % (len(prompt), MAX_CHARS))
    return prompt, "\n".join(notes)


class SYH3PromptBuilder:
    DESCRIPTION = "Builds one tidy prompt for a video model from style, world, action, timeline and spoken lines. Warns about mistakes."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "notes")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "style": ("STRING", {"default": "", "multiline": True, "tooltip": "The look of the clip, for example soft film light."}),
                "world": ("STRING", {"default": "", "multiline": True, "tooltip": "Where the scene happens and who is in it."}),
                "action": ("STRING", {"default": "", "multiline": True, "tooltip": "What happens in the clip. Write Picture 1, Picture 2 to point at input pictures."}),
                "picture_count": ("INT", {"default": 0, "min": 0, "max": 4, "tooltip": "How many input pictures you give the video model."}),
            },
            "optional": {
                "dialogue": ("STRING", {"default": "", "multiline": True, "tooltip": "Spoken lines, one per line. Each line gets its own speech tag."}),
                "dialogue_language": ("STRING", {"default": "", "multiline": False, "tooltip": "Language of the spoken lines, for example Japanese. Leave empty for none."}),
                "time_codes": ("STRING", {"default": "", "multiline": True, "tooltip": "One line per moment, like 0-4s: she turns round."}),
            },
        }

    def run(self, style, world, action, picture_count, dialogue="", dialogue_language="", time_codes=""):
        return build_prompt(style, world, action, dialogue, dialogue_language, picture_count, time_codes)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3PromptBuilder", SYH3PromptBuilder)
