"""Text Contains SY: tells whether a text holds a word or phrase."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


MATCH_MODES = ("the whole phrase", "any of the lines", "all of the lines")


def text_contains(text, needle, case_sensitive=False, whole_word=False, match=MATCH_MODES[0]):
    """Pure function. True when `needle` is inside `text`.
    match 'any of the lines' / 'all of the lines' treats every line of needle as its own word to look for.
    whole_word only counts a hit that is not part of a longer word (cat is not found in concatenate)."""
    return text_contains_info(text, needle, case_sensitive, whole_word, match)[0]


def text_contains_info(text, needle, case_sensitive=False, whole_word=False, match=MATCH_MODES[0]):
    """Pure function. Returns (found, found_list, missing_list)."""
    if not isinstance(text, str) or not isinstance(needle, str):
        raise ValueError("text and needle must be strings")
    if match not in MATCH_MODES:
        raise ValueError("match must be one of: %s" % ", ".join(MATCH_MODES))
    if needle.strip() == "" and needle == "":
        raise ValueError("needle is empty: type the word or phrase to look for")
    if match == MATCH_MODES[0]:
        words = [needle]
    else:
        words = [w.strip() for w in needle.splitlines() if w.strip()]
        if not words:
            raise ValueError("needle is empty: type one word or phrase per line")
    flags = 0 if case_sensitive else re.IGNORECASE
    found, missing = [], []
    for w in words:
        pattern = re.escape(w)
        if whole_word:
            pattern = r"(?<!\w)" + pattern + r"(?!\w)"
        (found if re.search(pattern, text, flags) else missing).append(w)
    if match == MATCH_MODES[2]:
        return (not missing), found, missing
    return bool(found), found, missing


def contains_info(found, found_list, missing_list):
    """Pure function. One plain line saying what was and was not found."""
    total = len(found_list) + len(missing_list)
    if total == 1:
        return "Found %r" % found_list[0] if found else "Not found: %r" % missing_list[0]
    line = "Found %d of %d: %s" % (len(found_list), total, ", ".join(found_list) if found_list else "none")
    if missing_list:
        line += "; missing: " + ", ".join(missing_list)
    return line


class SYTextContains:
    DESCRIPTION = ("Checks if a text contains a word or phrase. Gives true or false, and passes the text through. Can look for whole words only, "
                   "or check a list of words (any or all) and the info line says which were found and which are missing.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING", "STRING")
    RETURN_NAMES = ("contains", "text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to look in. It also comes out unchanged."}),
                "needle": ("STRING", {"default": "", "tooltip": "The word or phrase to look for."}),
                "case_sensitive": ("BOOLEAN", {"default": False, "tooltip": "On: upper and lower case must match exactly."}),
            },
            "optional": {
                "whole_word": ("BOOLEAN", {"default": False, "tooltip": "On: 'cat' is not found inside 'concatenate', only as a word of its own."}),
                "match": (list(MATCH_MODES), {"default": MATCH_MODES[0], "tooltip": "Use the lines of needle as separate words: true if any, or only if all, are in the text."}),
            },
        }

    def run(self, text, needle, case_sensitive=False, whole_word=False, match=MATCH_MODES[0]):
        found, hit, miss = text_contains_info(text, needle, case_sensitive, whole_word, match)
        return (found, text, contains_info(found, hit, miss))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextContains", SYTextContains)
NODE_DISPLAY_NAME_MAPPINGS["SYTextContains"] = "Text Contains SY"
