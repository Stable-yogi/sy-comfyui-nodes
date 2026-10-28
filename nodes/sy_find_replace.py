"""Find Replace SY: replace text, plain or with a regular expression, and count the changes."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_PATTERN = 500
MAX_INPUT = 1000000


def find_replace(text, find, replace, use_regex=False, case_sensitive=True):
    """Pure function. Returns (new_text, number_of_replacements)."""
    text = "" if text is None else str(text)
    find = "" if find is None else str(find)
    replace = "" if replace is None else str(replace)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    if len(find) > MAX_PATTERN:
        raise ValueError("find is too long: %d characters (limit %d)" % (len(find), MAX_PATTERN))
    if find == "":
        return text, 0
    flags = 0 if case_sensitive else re.IGNORECASE
    if use_regex:
        try:
            pattern = re.compile(find, flags)
        except re.error as e:
            raise ValueError("bad regular expression %r: %s" % (find, e))
        try:
            return pattern.subn(replace, text)
        except (re.error, IndexError) as e:
            raise ValueError("bad replacement %r: %s" % (replace, e))
    pattern = re.compile(re.escape(find), flags)
    return pattern.subn(lambda m: replace, text)


class SYFindReplace:
    DESCRIPTION = "Finds text and replaces it. Turn on use_regex for patterns. Also gives the number of replacements."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text you want to change."}),
                "find": ("STRING", {"default": "", "tooltip": "The words to look for in the text."}),
                "replace": ("STRING", {"default": "", "tooltip": "What to put in place of every match. Empty removes the match."}),
                "use_regex": ("BOOLEAN", {"default": False, "tooltip": "On: Find is a pattern (regex) for advanced matching. Off: plain words."}),
                "case_sensitive": ("BOOLEAN", {"default": True, "tooltip": "On: Cat and cat are different. Off: capital letters are ignored."}),
            }
        }

    def run(self, text, find, replace, use_regex=False, case_sensitive=True):
        return find_replace(text, find, replace, use_regex, case_sensitive)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FindReplace", SYFindReplace)
NODE_DISPLAY_NAME_MAPPINGS["SYFindReplace"] = "Find Replace SY"
