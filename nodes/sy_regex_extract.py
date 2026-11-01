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


def regex_extract(text, pattern, group=0, default="", ignore_case=False, find_all=False, join_with=", "):
    """Pure function. Returns (found_text, matched). On no match returns (default, False)."""
    return regex_extract_full(text, pattern, group, default, ignore_case, find_all, join_with)[:2]


def regex_extract_full(text, pattern, group=0, default="", ignore_case=False, find_all=False, join_with=", "):
    """Pure function. Returns (found_text, matched, info). find_all joins every match with join_with."""
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
    if find_all:
        pieces = [m.group(group) for m in rx.finditer(text) if m.group(group) is not None]
        if not pieces:
            return (default, False, _miss_info(text, pattern, ignore_case, default))
        return (str(join_with).join(pieces), True, "Found %d match(es) of group %d, joined with %r" % (len(pieces), group, str(join_with)))
    m = rx.search(text)
    if m is None or m.group(group) is None:
        return (default, False, _miss_info(text, pattern, ignore_case, default))
    found = m.group(group)
    return (found, True, "Matched group %d: %d character(s) at position %d" % (group, len(found), m.start(group)))


def _miss_info(text, pattern, ignore_case, default):
    line = "No match, so the default %s was returned" % (repr(default) if default else "(empty)")
    if not ignore_case:
        try:
            if re.search(pattern, text, re.IGNORECASE):
                line += "; it WOULD match if ignore_case is on"
        except re.error:
            pass
    return line


class SYRegexExtract:
    DESCRIPTION = ("Finds the first match of a regular expression in a text and gives one group of it, or a default. Can join all matches, "
                   "and the info line says where it matched or why not. Limits: pattern 200, text 100000 characters.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("result", "matched", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to search in (up to 100000 characters)."}),
                "pattern": ("STRING", {"default": "(\\d+)", "tooltip": "Regular expression to look for (up to 200 characters)."}),
                "group": ("INT", {"default": 1, "min": 0, "max": 99, "tooltip": "Which bracket group to return. 0 is the whole match."}),
                "default": ("STRING", {"default": "", "tooltip": "Text to return when nothing matches."}),
                "ignore_case": ("BOOLEAN", {"default": False, "tooltip": "Treat upper and lower case letters as the same."}),
            },
            "optional": {
                "find_all": ("BOOLEAN", {"default": False, "tooltip": "On: collect every match, not just the first, and join them."}),
                "join_with": ("STRING", {"default": ", ", "tooltip": "Put between matches when find_all is on, for example a comma or a new line."}),
            },
        }

    def run(self, text, pattern, group=1, default="", ignore_case=False, find_all=False, join_with=", "):
        return regex_extract_full(text, pattern, group, default, ignore_case, find_all, join_with)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RegexExtract", SYRegexExtract)
NODE_DISPLAY_NAME_MAPPINGS["SYRegexExtract"] = "Regex Extract SY"
