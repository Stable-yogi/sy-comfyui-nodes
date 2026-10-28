"""Text Contains SY: tells whether a text holds a word or phrase."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def text_contains(text, needle, case_sensitive=False):
    """Pure function. True when `needle` is inside `text`."""
    if not isinstance(text, str) or not isinstance(needle, str):
        raise ValueError("text and needle must be strings")
    if needle == "":
        raise ValueError("needle is empty: type the word or phrase to look for")
    if case_sensitive:
        return needle in text
    return needle.lower() in text.lower()


class SYTextContains:
    DESCRIPTION = "Checks if a text contains a word or phrase. Gives true or false, and passes the text through."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING")
    RETURN_NAMES = ("contains", "text")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to look in. It also comes out unchanged."}),
                "needle": ("STRING", {"default": "", "tooltip": "The word or phrase to look for."}),
                "case_sensitive": ("BOOLEAN", {"default": False, "tooltip": "On: upper and lower case must match exactly."}),
            }
        }

    def run(self, text, needle, case_sensitive=False):
        return (text_contains(text, needle, case_sensitive), text)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextContains", SYTextContains)
NODE_DISPLAY_NAME_MAPPINGS["SYTextContains"] = "Text Contains SY"
