"""Prompt Cleaner SY: removes repeated tags, double commas and extra spaces from a prompt, keeping the order."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_OPEN = "([{<"
_CLOSE = ")]}>"
_WRAP = re.compile(r"^[\(\[]+\s*(.*?)\s*(?::\s*[-+]?\d*\.?\d+\s*)?[\)\]]+$", re.S)


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


def tag_key(tag, case_insensitive=True, ignore_weights=False):
    """Pure function. The text two tags are compared by. ignore_weights makes (cat:1.2) and [cat] equal to cat."""
    key = tag
    if ignore_weights:
        m = _WRAP.match(tag)
        if m and m.group(1):
            key = m.group(1)
    key = re.sub(r"\s+", " ", key).strip()
    return key.lower() if case_insensitive else key


def clean_prompt_ex(text, case_insensitive=True, ignore_weights=False, drop_tags="", lowercase=False):
    """Pure function. Returns (text, repeats_removed, empty_removed, dropped).
    Tags are trimmed, empty ones dropped, repeats removed (first one wins), then joined with ', '."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    if not isinstance(drop_tags, str):
        raise ValueError("drop_tags must be text, got %s" % type(drop_tags).__name__)
    drop = {tag_key(t, case_insensitive, ignore_weights) for t in split_tags(drop_tags) if t.strip()}
    seen, out = set(), []
    repeats = empties = dropped = 0
    for tag in split_tags(text):
        tag = re.sub(r"\s+", " ", tag).strip()
        if tag == "":
            empties += 1
            continue
        if lowercase:
            tag = tag.lower()
        key = tag_key(tag, case_insensitive, ignore_weights)
        if key in drop:
            dropped += 1
            continue
        if key in seen:
            repeats += 1
            continue
        seen.add(key)
        out.append(tag)
    return ", ".join(out), repeats, empties, dropped


def clean_prompt(text, case_insensitive=True, ignore_weights=False, drop_tags="", lowercase=False):
    """Pure function. Trims tags, drops empty ones, removes repeats (first one wins), joins with ', '."""
    return clean_prompt_ex(text, case_insensitive, ignore_weights, drop_tags, lowercase)[0]


def cleaner_info(kept, repeats, empties, dropped):
    """Pure function. One plain line saying what was removed."""
    parts = []
    if repeats:
        parts.append("%d repeated" % repeats)
    if empties:
        parts.append("%d empty" % empties)
    if dropped:
        parts.append("%d dropped" % dropped)
    head = "Kept %d tag%s" % (kept, "" if kept == 1 else "s")
    return head + ("; removed " + ", ".join(parts) + "." if parts else "; nothing to remove.")


class SYPromptCleaner:
    DESCRIPTION = ("Cleans a comma separated prompt: removes repeated tags, double commas and extra spaces. The order stays the same. "
                   "Can treat (cat:1.2) as cat, drop tags you list, and lowercase everything. An info line says what was removed.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("text", "removed_count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The prompt to clean. Tags are split at commas."}),
                "case_insensitive": ("BOOLEAN", {"default": True, "tooltip": "On: 'Cat' and 'cat' count as the same tag. The first one stays."}),
            },
            "optional": {
                "ignore_weights": ("BOOLEAN", {"default": False, "tooltip": "On: (cat:1.2), [cat] and cat count as the same tag. The first one stays."}),
                "drop_tags": ("STRING", {"default": "", "tooltip": "Tags to remove, separated by commas. Matched the same way as repeats."}),
                "lowercase": ("BOOLEAN", {"default": False, "tooltip": "On: write every tag in lowercase."}),
            },
        }

    def run(self, text, case_insensitive=True, ignore_weights=False, drop_tags="", lowercase=False):
        out, repeats, empties, dropped = clean_prompt_ex(text, case_insensitive, ignore_weights, drop_tags, lowercase)
        kept = len(split_tags(out)) if out else 0
        return out, repeats + dropped, cleaner_info(kept, repeats, empties, dropped)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptCleaner", SYPromptCleaner)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptCleaner"] = "Prompt Cleaner SY"
