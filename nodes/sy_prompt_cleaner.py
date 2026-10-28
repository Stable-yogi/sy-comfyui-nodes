"""Prompt Cleaner SY: removes repeated tags, double commas and extra spaces from a prompt, keeping the order."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_OPEN = "([{<"
_CLOSE = ")]}>"


def split_tags(text):
    """Pure function. Splits on commas that are not inside brackets, so (a, b:1.2) stays one tag."""
    tags, depth, cur = [], 0, []
    for ch in text:
        if ch in _OPEN:
            depth += 1
        elif ch in _CLOSE:
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            tags.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    tags.append("".join(cur))
    return tags


def clean_prompt(text, case_insensitive=True):
    """Pure function. Trims tags, drops empty ones, removes repeats (first one wins), joins with ', '."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    seen, out = set(), []
    for tag in split_tags(text):
        tag = re.sub(r"\s+", " ", tag).strip()
        if tag == "":
            continue
        key = tag.lower() if case_insensitive else tag
        if key in seen:
            continue
        seen.add(key)
        out.append(tag)
    return ", ".join(out)


class SYPromptCleaner:
    DESCRIPTION = "Cleans a comma separated prompt: removes repeated tags, double commas and extra spaces. The order stays the same."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The prompt to clean. Tags are split at commas."}),
                "case_insensitive": ("BOOLEAN", {"default": True, "tooltip": "On: 'Cat' and 'cat' count as the same tag. The first one stays."}),
            }
        }

    def run(self, text, case_insensitive=True):
        return (clean_prompt(text, case_insensitive),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptCleaner", SYPromptCleaner)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptCleaner"] = "Prompt Cleaner SY"
