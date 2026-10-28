"""Text Repeat SY: repeats a piece of text several times with a separator."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_CHARS = 200000


def repeat_text(text, count, separator, numbered):
    """Pure function. Returns the repeated text; refuses to go over MAX_CHARS."""
    count = int(count)
    if count < 1 or count > 200:
        raise ValueError("count must be between 1 and 200, got %d" % count)
    text = str(text)
    separator = str(separator)
    parts = []
    size = 0
    for i in range(count):
        piece = ("%d. %s" % (i + 1, text)) if numbered else text
        size += len(piece) + (len(separator) if i else 0)
        if size > MAX_CHARS:
            raise ValueError("result would be longer than %d characters: use a shorter text or a smaller count" % MAX_CHARS)
        parts.append(piece)
    return separator.join(parts)


class SYTextRepeat:
    DESCRIPTION = "Repeats a text a number of times. It can put a separator between copies and number each copy."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to repeat."}),
                "count": ("INT", {"default": 2, "min": 1, "max": 200, "tooltip": "How many copies to make."}),
                "separator": ("STRING", {"default": "\n", "multiline": False, "tooltip": "Put between copies. Use a comma, a space or a new line."}),
                "numbered": ("BOOLEAN", {"default": False, "tooltip": "Start each copy with its number, like 1. text."}),
            }
        }

    def run(self, text, count, separator, numbered):
        return (repeat_text(text, count, separator, numbered),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextRepeat", SYTextRepeat)
