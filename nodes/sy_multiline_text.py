"""Multiline Text SY: a big text box. Lines that start with # are comments and are left out."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def strip_comments(text, keep_empty_lines=True):
    """Pure function. Removes lines whose first non-space character is #. A line starting with \\# keeps a literal #."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    out = []
    for line in text.split("\n"):
        line = line.rstrip("\r")
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if stripped.startswith("\\#"):
            line = line.replace("\\#", "#", 1)
        if not keep_empty_lines and line.strip() == "":
            continue
        out.append(line)
    return "\n".join(out)


def clean_lines(text, keep_empty_lines=True, trim_lines=False, collapse_spaces=False, drop_duplicate_lines=False, inline_comments=False):
    """Pure function. strip_comments plus optional tidying. Duplicate lines are matched ignoring case and edge spaces; the first one stays."""
    text = strip_comments(text, keep_empty_lines)
    if not (trim_lines or collapse_spaces or drop_duplicate_lines or inline_comments):
        return text
    out, seen = [], set()
    for line in text.split("\n"):
        if inline_comments:
            line = re.sub(r"(?<=\S)\s+#.*$", "", line)
        if trim_lines:
            line = line.strip()
        if collapse_spaces:
            line = re.sub(r"[ \t]{2,}", " ", line)
        if drop_duplicate_lines and line.strip():
            key = line.strip().lower()
            if key in seen:
                continue
            seen.add(key)
        out.append(line)
    return "\n".join(out)


def lines_info(raw, cleaned):
    """Pure function. Returns (line_count, plain info line)."""
    raw_n = len(str(raw).split("\n")) if str(raw) else 0
    out_n = len(cleaned.split("\n")) if cleaned else 0
    if out_n == raw_n:
        return out_n, "Kept all %d line%s." % (out_n, "" if out_n == 1 else "s")
    return out_n, "Kept %d of %d lines (%d left out)." % (out_n, raw_n, raw_n - out_n)


class SYMultilineText:
    DESCRIPTION = ("A big text box. Lines starting with # are notes to yourself and are left out. Start a line with \\# to keep a #. "
                   "Optional tidying: trim lines, collapse spaces, drop repeated lines, cut ' # note' endings. Also gives the line count.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("text", "line_count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "Your text. Lines that start with # are ignored."}),
                "keep_empty_lines": ("BOOLEAN", {"default": True, "tooltip": "Off: also remove empty lines from the result."}),
            },
            "optional": {
                "trim_lines": ("BOOLEAN", {"default": False, "tooltip": "On: remove spaces at the start and end of each line."}),
                "collapse_spaces": ("BOOLEAN", {"default": False, "tooltip": "On: turn runs of spaces inside a line into one space."}),
                "drop_duplicate_lines": ("BOOLEAN", {"default": False, "tooltip": "On: remove a line that already appeared (any case). Empty lines stay."}),
                "inline_comments": ("BOOLEAN", {"default": False, "tooltip": "On: cut the end of a line from ' #' onward, so 'a cat # old' becomes 'a cat'."}),
            },
        }

    def run(self, text, keep_empty_lines=True, trim_lines=False, collapse_spaces=False, drop_duplicate_lines=False, inline_comments=False):
        out = clean_lines(text, keep_empty_lines, trim_lines, collapse_spaces, drop_duplicate_lines, inline_comments)
        count, info = lines_info(text, out)
        return out, count, info


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MultilineText", SYMultilineText)
NODE_DISPLAY_NAME_MAPPINGS["SYMultilineText"] = "Multiline Text SY"
