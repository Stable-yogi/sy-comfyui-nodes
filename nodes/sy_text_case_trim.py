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


def _title(text):
    """Pure function. Title Case that does not capitalise the letter after an apostrophe ("don't" stays "Don't")."""
    return re.sub(r"[A-Za-z]+(?:['’][A-Za-z]+)*", lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), text)


def tidy_commas_line(line):
    """Pure function. 'a ,b,, c,' becomes 'a, b, c'. Commas inside numbers like 1,000 are left alone."""
    keep = "\x00"
    line = re.sub(r"(?<=\d),(?=\d)", keep, line)
    line = re.sub(r"\s*,(\s*,)*\s*", ", ", line)
    line = line.strip(" ,\t")
    return line.replace(keep, ",")


def case_trim(text, case="keep", trim=True, collapse_spaces=False, strip_empty_lines=False, tidy_commas=False):
    """Pure function. Applies the chosen steps in order: commas, spaces, trim, empty lines, case.
    tidy_commas fixes stray commas and spaces in a tag list, line by line."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    if case not in CASES:
        raise ValueError("case must be one of: %s" % ", ".join(CASES))
    out = text
    if tidy_commas:
        out = "\n".join(tidy_commas_line(line) if line.strip() else line for line in out.split("\n"))
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
        out = _title(out)
    elif case == "sentence":
        out = _sentence(out)
    return out


def case_info(before, after):
    """Pure function. One plain line: what the clean-up changed."""
    if before == after:
        return "No change: the text was already clean"
    return "Cleaned: %d -> %d characters, %d -> %d line(s)" % (len(before), len(after), len(before.splitlines()), len(after.splitlines()))


class SYTextCaseTrim:
    DESCRIPTION = ("Changes upper and lower case and cleans up text: trims each line, collapses double spaces, removes empty lines. "
                   "tidy_commas also fixes stray commas in a tag list ('a ,b,, c,' becomes 'a, b, c'). The info line says what changed.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to clean up."}),
                "case": (CASES, {"default": "keep", "tooltip": "Letter case: keep as is, UPPER, lower, Title Case or Sentence case."}),
                "trim": ("BOOLEAN", {"default": True, "tooltip": "Remove spaces at the start and end of the text and of every line."}),
                "collapse_spaces": ("BOOLEAN", {"default": False, "tooltip": "Turn several spaces in a row into one space."}),
                "strip_empty_lines": ("BOOLEAN", {"default": False, "tooltip": "Remove lines that are empty or hold only spaces."}),
            },
            "optional": {
                "tidy_commas": ("BOOLEAN", {"default": False, "tooltip": "On: fix stray commas and spaces in a tag list, like 'a ,b,, c,' to 'a, b, c'."}),
            },
        }

    def run(self, text, case="keep", trim=True, collapse_spaces=False, strip_empty_lines=False, tidy_commas=False):
        out = case_trim(text, case, trim, collapse_spaces, strip_empty_lines, tidy_commas)
        return (out, case_info(text, out))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextCaseTrim", SYTextCaseTrim)
NODE_DISPLAY_NAME_MAPPINGS["SYTextCaseTrim"] = "Text Case Trim SY"
