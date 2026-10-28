"""Text Between SY: cuts out the text that sits between two markers."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
WHICH = ("first", "last")


def text_between(text, start_marker, end_marker, which="first", include_markers=False, case_sensitive=True):
    """Pure function. Finds start..end pairs one after another (no overlap) and returns the first or last one."""
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
    flags = 0 if case_sensitive else re.IGNORECASE
    if not re.search(re.escape(start_marker), text, flags):
        raise ValueError("start_marker %r was not found in the text" % start_marker)
    pattern = re.compile(re.escape(start_marker) + "(.*?)" + re.escape(end_marker), flags | re.DOTALL)
    if which == "first":
        m = pattern.search(text)
    else:
        m = None
        for m in pattern.finditer(text):
            pass
    if m is None:
        raise ValueError("end_marker %r was not found after start_marker %r" % (end_marker, start_marker))
    return m.group(0) if include_markers else m.group(1)


class SYTextBetween:
    DESCRIPTION = "Cuts out the text between a start marker and an end marker. Stops with a clear error if a marker is missing."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

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
            }
        }

    def run(self, text, start_marker, end_marker, which="first", include_markers=False, case_sensitive=True):
        return (text_between(text, start_marker, end_marker, which, include_markers, case_sensitive),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextBetween", SYTextBetween)
NODE_DISPLAY_NAME_MAPPINGS["SYTextBetween"] = "Text Between SY"
