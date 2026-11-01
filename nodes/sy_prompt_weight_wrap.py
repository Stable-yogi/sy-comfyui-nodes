"""Prompt Weight Wrap SY: wraps a prompt in a weight or in brackets."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

STYLES = ["weight (text:1.2)", "round ( )", "double round (( ))", "square [ ]", "curly { }"]
ALREADY = ["wrap again", "replace the weight", "leave as it is"]
_WEIGHTED = re.compile(r"^\((.*):(-?\d+(?:\.\d+)?)\)$", re.S)


def split_tags(text):
    """Pure function. Splits at commas that are not inside ( ) [ ] { }. Empty pieces are dropped."""
    parts, cur, depth = [], [], 0
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur).strip())
    return [p for p in parts if p]


def _wrap_one(text, style, weight):
    if style == STYLES[0]:
        if weight == 1.0:
            return text
        return "(%s:%s)" % (text, ("%.3f" % weight).rstrip("0").rstrip("."))
    if style == STYLES[1]:
        return "(%s)" % text
    if style == STYLES[2]:
        return "((%s))" % text
    if style == STYLES[3]:
        return "[%s]" % text
    return "{%s}" % text


def wrap_prompt(text, style="weight (text:1.2)", weight=1.2, each_tag=False, already="wrap again"):
    """Pure function. Empty text stays empty. A weight of exactly 1 leaves the text as it is.
    each_tag wraps every comma tag on its own. already says what to do with text that is already like (cat:1.3)."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    if style not in STYLES:
        raise ValueError("style must be one of: %s" % ", ".join(STYLES))
    if already not in ALREADY:
        raise ValueError("already must be one of: %s" % ", ".join(ALREADY))
    text = text.strip()
    if text == "":
        return ""
    if style == STYLES[0]:
        weight = float(weight)
        if weight != weight or weight < 0 or weight > 10:
            raise ValueError("weight must be between 0 and 10, got %s" % weight)
    units = split_tags(text) if each_tag else [text]
    if not units:
        return ""
    out = []
    for unit in units:
        found = _WEIGHTED.match(unit)
        if found and already == ALREADY[2]:
            out.append(unit)
            continue
        if found and already == ALREADY[1]:
            unit = found.group(1).strip()
        out.append(_wrap_one(unit, style, weight))
    return ", ".join(out)


def wrap_info(text, result, style, weight, each_tag=False):
    """Pure function. One plain line: what was done, plus warnings about brackets and strong weights."""
    text = text.strip() if isinstance(text, str) else ""
    if not text:
        return "Empty text: nothing to wrap"
    count = len(split_tags(text)) if each_tag else 1
    how = "Wrapped %d tag(s) one by one" % count if each_tag else "Wrapped the whole text"
    line = "%s as %s" % (how, style.split(" ")[0] if style != STYLES[0] else "(text:%s)" % ("%.3f" % float(weight)).rstrip("0").rstrip("."))
    for a, b, name in (("(", ")", "round"), ("[", "]", "square"), ("{", "}", "curly")):
        if text.count(a) != text.count(b):
            line += "; WARNING: the %s brackets in the text do not match" % name
    if style == STYLES[0] and float(weight) > 1.5:
        line += "; WARNING: weights above 1.5 often burn or distort the picture"
    return line


class SYPromptWeightWrap:
    DESCRIPTION = ("Wraps a prompt as (text:1.2) with a weight, or in round, square or curly brackets. Can wrap every tag on its own, "
                   "avoids double wrapping like ((cat:1.2):1.2), and warns about unmatched brackets.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The prompt part to wrap."}),
                "style": (STYLES, {"default": STYLES[0], "tooltip": "How to wrap: with a weight number or with a bracket type."}),
                "weight": ("FLOAT", {"default": 1.2, "min": 0.0, "max": 10.0, "step": 0.05, "tooltip": "Strength for the weight style. 1 means no change."}),
            },
            "optional": {
                "each_tag": ("BOOLEAN", {"default": False, "tooltip": "On: wrap every comma tag on its own, like (cat:1.2), (dog:1.2)."}),
                "already_weighted": (ALREADY, {"default": ALREADY[0], "tooltip": "What to do with a tag already written like (cat:1.3): wrap again, change its weight, or skip it."}),
            },
        }

    def run(self, text, style=STYLES[0], weight=1.2, each_tag=False, already_weighted=ALREADY[0]):
        out = wrap_prompt(text, style, weight, each_tag, already_weighted)
        return (out, wrap_info(text, out, style, weight, each_tag))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptWeightWrap", SYPromptWeightWrap)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptWeightWrap"] = "Prompt Weight Wrap SY"
