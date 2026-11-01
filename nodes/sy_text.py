"""Text SY: a multiline text box that passes its text on, with an option to clean line ends."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


_INVISIBLE = "\u200b\u200c\u200d\u2060\ufeff"


def count_invisible(text):
    """Pure function. Counts zero-width characters and non-breaking spaces (they sneak in when you paste from a web page)."""
    return sum(text.count(c) for c in _INVISIBLE) + text.count("\u00a0")


def clean_text(text, strip_lines=False, clean_invisible=False, strip_ends=False):
    """Pure function. Returns the text unchanged, or with trailing spaces removed per line.
    clean_invisible removes zero-width characters and turns non-breaking spaces into normal spaces.
    strip_ends removes empty lines and spaces at the very start and end."""
    if text is None:
        text = ""
    text = str(text)
    if clean_invisible:
        for c in _INVISIBLE:
            text = text.replace(c, "")
        text = text.replace("\u00a0", " ")
    if strip_lines:
        text = "\n".join(line.rstrip(" \t\r") for line in text.split("\n"))
    if strip_ends:
        text = text.strip()
    return text


def text_info(original, result):
    """Pure function. One plain line: size of the result, and a warning about hidden characters."""
    original = "" if original is None else str(original)
    line = "%d character(s), %d line(s), about %d tokens" % (len(result), len(result.splitlines()), -(-len(result) // 4))
    hidden = count_invisible(result)
    if hidden:
        line += "; WARNING: %d hidden character(s) (zero-width or non-breaking space) - turn on clean_invisible" % hidden
    elif count_invisible(original):
        line += "; removed %d hidden character(s)" % count_invisible(original)
    return line


class SYText:
    DESCRIPTION = ("A multiline text box. The text goes out as it is. Optional clean-up: spaces at line ends, empty lines at the start and end, "
                   "and hidden characters that sneak in when you paste from a web page. The info line shows the size.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to pass on, such as your prompt."}),
                "strip_lines": ("BOOLEAN", {"default": False, "tooltip": "On: trim spaces at the start and end of every line."}),
            },
            "optional": {
                "clean_invisible": ("BOOLEAN", {"default": False, "tooltip": "On: remove zero-width characters and turn non-breaking spaces into normal spaces."}),
                "strip_ends": ("BOOLEAN", {"default": False, "tooltip": "On: remove empty lines and spaces at the very start and end of the text."}),
            },
        }

    def run(self, text, strip_lines=False, clean_invisible=False, strip_ends=False):
        out = clean_text(text, strip_lines, clean_invisible, strip_ends)
        return (out, text_info(text, out))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Text", SYText)
