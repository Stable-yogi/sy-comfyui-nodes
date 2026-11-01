"""Text Repeat SY: repeats a piece of text several times with a separator."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_CHARS = 200000


def repeat_text(text, count, separator, numbered, start_at=1):
    """Pure function. Returns the repeated text; refuses to go over MAX_CHARS. start_at is the first number when numbered."""
    count = int(count)
    if count < 1 or count > 200:
        raise ValueError("count must be between 1 and 200, got %d" % count)
    text = str(text)
    separator = str(separator)
    parts = []
    size = 0
    for i in range(count):
        piece = ("%d. %s" % (i + int(start_at), text)) if numbered else text
        size += len(piece) + (len(separator) if i else 0)
        if size > MAX_CHARS:
            raise ValueError("result would be longer than %d characters: use a shorter text or a smaller count" % MAX_CHARS)
        parts.append(piece)
    return separator.join(parts)


def repeat_info(text, count, result):
    """Pure function. One plain line: copies made and the size of the result."""
    line = "%d cop%s of %d character(s), %d characters in all, about %d tokens" % (
        int(count), "y" if int(count) == 1 else "ies", len(str(text)), len(result), -(-len(result) // 4))
    if str(text) == "":
        line += "; WARNING: the text is empty, so only separators come out"
    return line


class SYTextRepeat:
    DESCRIPTION = ("Repeats a text a number of times. It can put a separator between copies and number each copy, starting at any number. "
                   "Refuses results over 200000 characters, and the info line shows the size.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to repeat."}),
                "count": ("INT", {"default": 2, "min": 1, "max": 200, "tooltip": "How many copies to make."}),
                "separator": ("STRING", {"default": "\n", "multiline": False, "tooltip": "Put between copies. Use a comma, a space or a new line."}),
                "numbered": ("BOOLEAN", {"default": False, "tooltip": "Start each copy with its number, like 1. text."}),
            },
            "optional": {
                "start_at": ("INT", {"default": 1, "min": 0, "max": 1000000, "tooltip": "First number when numbered is on. Use 0 to count from zero."}),
            },
        }

    def run(self, text, count, separator, numbered, start_at=1):
        out = repeat_text(text, count, separator, numbered, start_at)
        return (out, repeat_info(text, count, out))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextRepeat", SYTextRepeat)
