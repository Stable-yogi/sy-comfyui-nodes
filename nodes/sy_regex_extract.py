"""Regex Extract SY: finds the first match of a pattern in a text and returns one group."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_PATTERN = 200
MAX_TEXT = 100000
# a group that repeats inside a repeat, like (a+)+ , can freeze the match
_NESTED_REPEAT = re.compile(r"\([^()]*[+*][^()]*\)\s*[+*{]")


def regex_extract(text, pattern, group=0, default="", ignore_case=False):
    """Pure function. Returns (found_text, matched). On no match returns (default, False)."""
    if not isinstance(text, str) or not isinstance(pattern, str):
        raise ValueError("text and pattern must be strings")
    if pattern == "":
        raise ValueError("pattern is empty: type a regular expression")
    if len(pattern) > MAX_PATTERN:
        raise ValueError("pattern is too long (%d characters): keep it under %d" % (len(pattern), MAX_PATTERN))
    if len(text) > MAX_TEXT:
        raise ValueError("text is too long (%d characters): keep it under %d" % (len(text), MAX_TEXT))
    if _NESTED_REPEAT.search(pattern):
        raise ValueError("pattern repeats a repeated group, which can freeze ComfyUI: write it more simply")
    group = int(group)
    if group < 0:
        raise ValueError("group must be 0 or more, got %d" % group)
    try:
        rx = re.compile(pattern, re.IGNORECASE if ignore_case else 0)
    except re.error as e:
        raise ValueError("pattern is not a valid regular expression: %s" % e)
    if group > rx.groups:
        raise ValueError("group %d does not exist: the pattern has %d group(s)" % (group, rx.groups))
    m = rx.search(text)
    if m is None:
        return (default, False)
    found = m.group(group)
    if found is None:
        return (default, False)
    return (found, True)


class SYRegexExtract:
    DESCRIPTION = "Finds the first match of a regular expression in a text and gives one group of it, or a default. Limits: pattern 200, text 100000 characters."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("result", "matched")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to search in (up to 100000 characters)."}),
                "pattern": ("STRING", {"default": "(\\d+)", "tooltip": "Regular expression to look for (up to 200 characters)."}),
                "group": ("INT", {"default": 1, "min": 0, "max": 99, "tooltip": "Which bracket group to return. 0 is the whole match."}),
                "default": ("STRING", {"default": "", "tooltip": "Text to return when nothing matches."}),
                "ignore_case": ("BOOLEAN", {"default": False, "tooltip": "Treat upper and lower case letters as the same."}),
            }
        }

    def run(self, text, pattern, group=1, default="", ignore_case=False):
        return regex_extract(text, pattern, group, default, ignore_case)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RegexExtract", SYRegexExtract)
NODE_DISPLAY_NAME_MAPPINGS["SYRegexExtract"] = "Regex Extract SY"
