"""Text Split Lines SY: splits text into lines and picks one line by number, wrapping around."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def split_lines(text, skip_empty=True):
    """Pure function. Returns the list of lines."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    lines = text.splitlines()
    if skip_empty:
        lines = [x for x in lines if x.strip() != ""]
    return lines


def pick_line(lines, index):
    """Pure function. Picks a line by index; too big or negative numbers wrap around."""
    if not lines:
        raise ValueError("there are no lines to pick from: add some text or turn off skip_empty")
    return lines[int(index) % len(lines)]


class SYTextSplitLines:
    DESCRIPTION = "Splits text into lines. Gives the full list, one line picked by number (wraps around), and the line count."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("lines", "line", "count")
    OUTPUT_IS_LIST = (True, False, False)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to split. One line becomes one item."}),
                "index": ("INT", {"default": 0, "min": -(2 ** 31), "max": 2 ** 31 - 1, "tooltip": "Which line to pick, counting from 0. Too big a number wraps to the start."}),
                "skip_empty": ("BOOLEAN", {"default": True, "tooltip": "Leave out empty lines and lines with only spaces."}),
            }
        }

    def run(self, text, index=0, skip_empty=True):
        lines = split_lines(text, skip_empty)
        return (lines, pick_line(lines, index), len(lines))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextSplitLines", SYTextSplitLines)
NODE_DISPLAY_NAME_MAPPINGS["SYTextSplitLines"] = "Text Split Lines SY"
