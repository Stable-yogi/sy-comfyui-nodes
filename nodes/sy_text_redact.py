"""Text Redact SY: hides chosen words or patterns (names, emails, numbers) before text is shared."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

ALSO = ("nothing", "email addresses", "phone-like numbers", "web links", "all of these")
STYLES = ("block characters", "[REDACTED]", "same length stars", "custom")
BLOCK = "█" * 5   # a fixed-size block, so the hidden length is not given away

# These three patterns are simple on purpose. They catch the common cases, not every possible one.
_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}")
_LINK = re.compile(r"(?:https?://|www\.)[^\s<>\"']*[^\s<>\"'.,;:!?)\]]")
_PHONE = re.compile(r"(?<![\w])\+?\d[\d\s().\-]{5,}\d(?![\w])")


def _word_pattern(words, whole_words, ignore_case):
    """Builds one regex from the word list, longest phrase first. None if the list is empty."""
    seen, cleaned = set(), []
    for line in words.splitlines():
        w = line.strip()
        if w and w not in seen:
            seen.add(w)
            cleaned.append(w)
    if not cleaned:
        return None
    cleaned.sort(key=lambda w: (-len(w), w))
    parts = []
    for w in cleaned:
        p = re.escape(w)
        if whole_words:
            if re.match(r"\w", w[0]):
                p = r"(?<!\w)" + p
            if re.match(r"\w", w[-1]):
                p = p + r"(?!\w)"
        parts.append(p)
    return re.compile("|".join(parts), re.IGNORECASE if ignore_case else 0)


def _replacement(matched, style, custom):
    if style == "block characters":
        return BLOCK
    if style == "[REDACTED]":
        return "[REDACTED]"
    if style == "same length stars":
        return "*" * len(matched)
    return custom


def redact(text, words, also_hide, style, custom, whole_words, ignore_case):
    """Pure function. Returns (new_text, hidden_count). Every hidden piece counts once, even if two rules hit it.
    The email, phone-like and link patterns are simple and not perfect: always read the result before sharing.
    Phone-like means 7 or more digits with spaces, dots, dashes or brackets between, so some dates also match."""
    if not isinstance(text, str):
        raise ValueError("text must be text")
    if also_hide not in ALSO:
        raise ValueError("also_hide must be one of: %s (got %r)" % (", ".join(ALSO), also_hide))
    if style not in STYLES:
        raise ValueError("replace_with must be one of: %s (got %r)" % (", ".join(STYLES), style))
    spans = []
    wp = _word_pattern(words or "", whole_words, ignore_case)
    if wp is not None:
        spans += [(m.start(), m.end()) for m in wp.finditer(text)]
    if also_hide in ("email addresses", "all of these"):
        spans += [(m.start(), m.end()) for m in _EMAIL.finditer(text)]
    if also_hide in ("web links", "all of these"):
        spans += [(m.start(), m.end()) for m in _LINK.finditer(text)]
    if also_hide in ("phone-like numbers", "all of these"):
        spans += [(m.start(), m.end()) for m in _PHONE.finditer(text)
                  if sum(c.isdigit() for c in m.group(0)) >= 7]
    if not spans:
        return (text, 0)
    spans.sort()
    merged = [list(spans[0])]
    for s, e in spans[1:]:
        if s < merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    out, pos = [], 0
    for s, e in merged:
        out.append(text[pos:s])
        out.append(_replacement(text[s:e], style, custom))
        pos = e
    out.append(text[pos:])
    return ("".join(out), len(merged))


class SYTextRedact:
    DESCRIPTION = ("Hides chosen words or phrases, and optionally emails, phone-like numbers and web links, before "
                   "you share a text. The patterns are simple, so read the result. Nothing is sent anywhere.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "hidden_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to clean before sharing it."}),
                "words": ("STRING", {"multiline": True, "default": "", "tooltip": "Words or phrases to hide, one per line. Blank lines are skipped."}),
                "also_hide": (list(ALSO), {"default": "nothing", "tooltip": "Also hide email addresses, phone-like numbers or web links. The patterns are simple, not perfect."}),
                "replace_with": (list(STYLES), {"default": "block characters", "tooltip": "What goes in place of hidden text. Block characters have a fixed size, stars keep the length."}),
                "custom": ("STRING", {"default": "***", "tooltip": "The text used when replace_with is custom."}),
                "whole_words_only": ("BOOLEAN", {"default": True, "tooltip": "On: Ann does not hide the start of Annual. Off: any match is hidden."}),
                "ignore_case": ("BOOLEAN", {"default": True, "tooltip": "On: ann also matches Ann and ANN."}),
            }
        }

    def run(self, text, words, also_hide, replace_with, custom, whole_words_only, ignore_case):
        return redact(text, words, also_hide, replace_with, custom, whole_words_only, ignore_case)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextRedact", SYTextRedact)
NODE_DISPLAY_NAME_MAPPINGS["SYTextRedact"] = "Text Redact SY"
