"""Text Truncate SY: shortens a text to a maximum length and adds a short ending."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_TRAIL = " \t\r\n,;:"


def truncate_text(text, max_chars, suffix, at_word):
    """Pure function. Returns (text, truncated). The result with the suffix is at most max_chars long."""
    if not 1 <= max_chars <= 100000:
        raise ValueError("max_chars must be between 1 and 100000, got %s" % max_chars)
    if len(text) <= max_chars:
        return (text, False)
    if len(suffix) > max_chars:
        raise ValueError("suffix is longer than max_chars; shorten the suffix or raise max_chars")
    limit = max_chars - len(suffix)
    cut = text[:limit]
    if at_word and not text[limit].isspace():
        idx = max(cut.rfind(" "), cut.rfind("\n"), cut.rfind("\t"))
        if idx > 0:
            cut = cut[:idx]
    cut = cut.rstrip(_TRAIL)
    return (cut + suffix, True)


class SYTextTruncate:
    DESCRIPTION = "Shortens a text to a maximum length and adds an ending such as three dots. Can cut at a word end."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("text", "truncated")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to shorten."}),
                "max_chars": ("INT", {"default": 100, "min": 1, "max": 100000, "tooltip": "Longest allowed result, counting the ending."}),
                "suffix": ("STRING", {"default": "...", "tooltip": "Added at the end when the text was cut. Leave empty for none."}),
                "at_word": ("BOOLEAN", {"default": True, "tooltip": "On: cut back to the end of a whole word. Off: cut at the exact character."}),
            }
        }

    def run(self, text, max_chars, suffix, at_word):
        return truncate_text(text, max_chars, suffix, at_word)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextTruncate", SYTextTruncate)
NODE_DISPLAY_NAME_MAPPINGS["SYTextTruncate"] = "Text Truncate SY"
