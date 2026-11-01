"""Text Between SY: cuts out the text that sits between two markers."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
WHICH = ("first", "last")
IF_MISSING = ("stop with an error", "give empty text", "give the whole text")


def text_between(text, start_marker, end_marker, which="first", include_markers=False, case_sensitive=True,
                 if_missing="stop with an error", trim_result=False):
    """Pure function. Finds start..end pairs one after another (no overlap) and returns the first or last one.
    if_missing says what to do when a marker is not found. trim_result removes spaces and empty lines around the result."""
    return text_between_info(text, start_marker, end_marker, which, include_markers, case_sensitive, if_missing, trim_result)[0]


def text_between_info(text, start_marker, end_marker, which="first", include_markers=False, case_sensitive=True,
                      if_missing="stop with an error", trim_result=False):
    """Pure function. Returns (result, info)."""
    text = "" if text is None else str(text)
    start_marker = "" if start_marker is None else str(start_marker)
    end_marker = "" if end_marker is None else str(end_marker)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    if start_marker == "":
        raise ValueError("start_marker is empty: type the text that comes before the part you want")
    if end_marker == "":
        raise ValueError("end_marker is empty: type the text that comes after the part you want")
    if which not in WHICH:
        raise ValueError("unknown which %r: choose first or last" % (which,))
    if if_missing not in IF_MISSING:
        raise ValueError("if_missing must be one of: %s" % ", ".join(IF_MISSING))
    flags = 0 if case_sensitive else re.IGNORECASE
    problem = None
    m = None
    if not re.search(re.escape(start_marker), text, flags):
        problem = "start_marker %r was not found in the text" % start_marker
        if case_sensitive and re.search(re.escape(start_marker), text, re.IGNORECASE):
            problem += " (it exists in other letter case: turn off case_sensitive)"
    else:
        pattern = re.compile(re.escape(start_marker) + "(.*?)" + re.escape(end_marker), flags | re.DOTALL)
        if which == "first":
            m = pattern.search(text)
        else:
            m = None
            for m in pattern.finditer(text):
                pass
        if m is None:
            problem = "end_marker %r was not found after start_marker %r" % (end_marker, start_marker)
    if problem:
        if if_missing == IF_MISSING[0]:
            raise ValueError(problem)
        if if_missing == IF_MISSING[1]:
            return "", "Not found, gave empty text: " + problem
        return text, "Not found, gave the whole text: " + problem
    found = m.group(0) if include_markers else m.group(1)
    if trim_result:
        found = found.strip()
    return found, "Found the %s pair of markers; %d character(s) at position %d" % (which, len(found), m.start())


class SYTextBetween:
    DESCRIPTION = ("Cuts out the text between a start marker and an end marker, for example to pull an answer out of chatty model output. "
                   "A missing marker stops with a clear error, or gives empty or the whole text if you choose. Can trim the result.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to search in."}),
                "start_marker": ("STRING", {"default": "", "tooltip": "The text just before the part you want."}),
                "end_marker": ("STRING", {"default": "", "tooltip": "The text just after the part you want."}),
                "which": (list(WHICH), {"default": "first", "tooltip": "If the pair appears many times: take the first one or the last one."}),
                "include_markers": ("BOOLEAN", {"default": False, "tooltip": "On: keep the start and end markers in the result."}),
                "case_sensitive": ("BOOLEAN", {"default": True, "tooltip": "On: capital letters must match. Off: they are ignored."}),
            },
            "optional": {
                "if_missing": (list(IF_MISSING), {"default": IF_MISSING[0], "tooltip": "When a marker is not found: stop with an error, give empty text, or pass the whole text through."}),
                "trim_result": ("BOOLEAN", {"default": False, "tooltip": "On: remove spaces and empty lines around the result."}),
            },
        }

    def run(self, text, start_marker, end_marker, which="first", include_markers=False, case_sensitive=True,
            if_missing=IF_MISSING[0], trim_result=False):
        return text_between_info(text, start_marker, end_marker, which, include_markers, case_sensitive, if_missing, trim_result)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextBetween", SYTextBetween)
NODE_DISPLAY_NAME_MAPPINGS["SYTextBetween"] = "Text Between SY"
