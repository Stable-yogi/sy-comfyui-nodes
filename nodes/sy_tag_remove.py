"""Tag Remove SY: takes unwanted tags or words out of a comma separated prompt."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MATCH_MODES = ["exact tag", "tag contains word"]
_WEIGHTED = re.compile(r"^\(+\s*(.*?)\s*(?::\s*-?[0-9.]+)?\s*\)+$")


def split_entries(raw):
    """Pure function. Splits a remove list (one per line or comma separated) into clean entries."""
    out = []
    for part in str(raw or "").replace("\r", "\n").replace("\n", ",").split(","):
        part = part.strip()
        if part:
            out.append(part)
    return out


def _inner(tag):
    """Tag without weight brackets: (red:1.2) -> red."""
    m = _WEIGHTED.match(tag)
    return m.group(1).strip() if m else tag


def _has_word(tag, entry, flags):
    pattern = r"(?<!\w)" + re.escape(entry) + r"(?!\w)"
    return re.search(pattern, tag, flags) is not None


def remove_tags(text, remove_list, match="exact tag", ignore_case=True):
    """Pure function. Returns (kept_text, removed_list). Order is kept, tags are joined with ', '."""
    if match not in MATCH_MODES:
        raise ValueError("match must be one of: %s (got %r)" % (", ".join(MATCH_MODES), match))
    entries = [e for e in (str(x).strip() for x in remove_list) if e]
    flags = re.IGNORECASE if ignore_case else 0
    tags = [t.strip() for t in str(text or "").replace("\n", " ").split(",")]
    tags = [t for t in tags if t]
    kept, removed = [], []
    for tag in tags:
        hit = False
        inner = _inner(tag)
        for e in entries:
            if match == "exact tag":
                a, b, c = (inner.lower(), e.lower(), tag.lower()) if ignore_case else (inner, e, tag)
                hit = (a == b) or (c == b)
            else:
                hit = _has_word(tag, e, flags)
            if hit:
                break
        (removed if hit else kept).append(tag)
    return ", ".join(kept), removed


class SYTagRemove:
    DESCRIPTION = ("Takes unwanted tags or words out of a comma separated prompt. Keeps the order of the rest "
                   "and tells you what it removed.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("text", "removed", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The prompt, tags separated by commas."}),
                "remove": ("STRING", {"multiline": True, "default": "", "tooltip": "Tags to take out. One per line or separated by commas."}),
                "match": (MATCH_MODES, {"default": "exact tag", "tooltip": "Exact tag: whole tag must match. Contains word: the word may sit inside a longer tag."}),
                "ignore_case": ("BOOLEAN", {"default": True, "tooltip": "On: Red and red count as the same."}),
            }
        }

    def run(self, text, remove, match="exact tag", ignore_case=True):
        kept, removed = remove_tags(text, split_entries(remove), match, ignore_case)
        return (kept, ", ".join(removed), len(removed))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TagRemove", SYTagRemove)
NODE_DISPLAY_NAME_MAPPINGS["SYTagRemove"] = "Tag Remove SY"
