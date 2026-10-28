"""Text SY: a multiline text box that passes its text on, with an option to clean line ends."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def clean_text(text, strip_lines=False):
    """Pure function. Returns the text unchanged, or with trailing spaces removed per line."""
    if text is None:
        text = ""
    text = str(text)
    if not strip_lines:
        return text
    return "\n".join(line.rstrip(" \t\r") for line in text.split("\n"))


class SYText:
    DESCRIPTION = "A multiline text box. The text goes out as it is. Turn on strip_lines to remove spaces at the end of each line."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to pass on, such as your prompt."}),
                "strip_lines": ("BOOLEAN", {"default": False, "tooltip": "On: trim spaces at the start and end of every line."}),
            }
        }

    def run(self, text, strip_lines=False):
        return (clean_text(text, strip_lines),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Text", SYText)
