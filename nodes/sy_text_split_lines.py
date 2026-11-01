"""Text Split Lines SY: splits text into lines and picks one line by number, wrapping around."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def split_lines(text, skip_empty=True, trim_lines=False, skip_comments=False):
    """Pure function. Returns the list of lines. trim_lines removes spaces around each line.
    skip_comments leaves out lines that start with # (handy for wildcard files)."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    lines = text.splitlines()
    if trim_lines:
        lines = [x.strip() for x in lines]
    if skip_comments:
        lines = [x for x in lines if not x.lstrip().startswith("#")]
    if skip_empty:
        lines = [x for x in lines if x.strip() != ""]
    return lines


def pick_line(lines, index):
    """Pure function. Picks a line by index; too big or negative numbers wrap around."""
    if not lines:
        raise ValueError("there are no lines to pick from: add some text or turn off skip_empty")
    return lines[int(index) % len(lines)]


def lines_info(count, index):
    """Pure function. One plain line: how many lines and which one was picked."""
    real = int(index) % count
    line = "%d line(s); picked line %d (index %d)" % (count, real + 1, real)
    if real != int(index):
        line += ", index %d wrapped around" % int(index)
    return line


class SYTextSplitLines:
    DESCRIPTION = ("Splits text into lines. Gives the full list, one line picked by number (wraps around), and the line count. "
                   "Can trim spaces and skip # comment lines, and the info line says which line was picked.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT", "STRING")
    RETURN_NAMES = ("lines", "line", "count", "info")
    OUTPUT_IS_LIST = (True, False, False, False)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to split. One line becomes one item."}),
                "index": ("INT", {"default": 0, "min": -(2 ** 31), "max": 2 ** 31 - 1, "tooltip": "Which line to pick, counting from 0. Too big a number wraps to the start."}),
                "skip_empty": ("BOOLEAN", {"default": True, "tooltip": "Leave out empty lines and lines with only spaces."}),
            },
            "optional": {
                "trim_lines": ("BOOLEAN", {"default": False, "tooltip": "On: remove spaces at the start and end of every line."}),
                "skip_comments": ("BOOLEAN", {"default": False, "tooltip": "On: lines that start with # are left out."}),
            },
        }

    def run(self, text, index=0, skip_empty=True, trim_lines=False, skip_comments=False):
        lines = split_lines(text, skip_empty, trim_lines, skip_comments)
        return (lines, pick_line(lines, index), len(lines), lines_info(len(lines), index))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextSplitLines", SYTextSplitLines)
NODE_DISPLAY_NAME_MAPPINGS["SYTextSplitLines"] = "Text Split Lines SY"
