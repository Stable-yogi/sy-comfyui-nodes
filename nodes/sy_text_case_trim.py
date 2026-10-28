"""Text Case Trim SY: changes letter case and cleans spaces and empty lines."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

CASES = ["keep", "upper", "lower", "title", "sentence"]


def _sentence(text):
    text = text.lower()
    return re.sub(r"(^|[.!?]\s+|\n\s*)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)


def case_trim(text, case="keep", trim=True, collapse_spaces=False, strip_empty_lines=False):
    """Pure function. Applies the chosen steps in order: spaces, trim, empty lines, case."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    if case not in CASES:
        raise ValueError("case must be one of: %s" % ", ".join(CASES))
    out = text
    if collapse_spaces:
        out = "\n".join(re.sub(r"[ \t]+", " ", line) for line in out.split("\n"))
    if trim:
        out = "\n".join(line.strip() for line in out.split("\n")).strip()
    if strip_empty_lines:
        out = "\n".join(line for line in out.split("\n") if line.strip() != "")
    if case == "upper":
        out = out.upper()
    elif case == "lower":
        out = out.lower()
    elif case == "title":
        out = out.title()
    elif case == "sentence":
        out = _sentence(out)
    return out


class SYTextCaseTrim:
    DESCRIPTION = "Changes upper and lower case and cleans up text: trims each line, collapses double spaces, removes empty lines."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to clean up."}),
                "case": (CASES, {"default": "keep", "tooltip": "Letter case: keep as is, UPPER, lower, Title Case or Sentence case."}),
                "trim": ("BOOLEAN", {"default": True, "tooltip": "Remove spaces at the start and end of the text and of every line."}),
                "collapse_spaces": ("BOOLEAN", {"default": False, "tooltip": "Turn several spaces in a row into one space."}),
                "strip_empty_lines": ("BOOLEAN", {"default": False, "tooltip": "Remove lines that are empty or hold only spaces."}),
            }
        }

    def run(self, text, case="keep", trim=True, collapse_spaces=False, strip_empty_lines=False):
        return (case_trim(text, case, trim, collapse_spaces, strip_empty_lines),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextCaseTrim", SYTextCaseTrim)
NODE_DISPLAY_NAME_MAPPINGS["SYTextCaseTrim"] = "Text Case Trim SY"
