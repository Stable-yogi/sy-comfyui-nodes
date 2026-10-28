"""Line Pick SY: takes one line out of a multi-line text by its number."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def line_pick(text, index, skip_blank):
    """Pure function. Returns (line, total). A negative index counts from the end."""
    lines = str(text).splitlines()
    if skip_blank:
        lines = [x for x in lines if x.strip()]
    total = len(lines)
    index = int(index)
    if total == 0:
        raise ValueError("text has no lines to pick from")
    if index >= total or index < -total:
        raise ValueError("index %d is out of range: the text has %d lines (use %d to %d)" % (index, total, -total, total - 1))
    return lines[index], total


class SYLinePick:
    DESCRIPTION = "Takes one line from a text. Count from the top with 0, 1, 2 or from the bottom with -1, -2."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("line", "total_lines")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text with several lines."}),
                "index": ("INT", {"default": 0, "min": -100000, "max": 100000, "tooltip": "Line to take, counting from 0. Negative counts from the end."}),
                "skip_blank": ("BOOLEAN", {"default": True, "tooltip": "Ignore empty lines when counting."}),
            }
        }

    def run(self, text, index, skip_blank):
        return line_pick(text, index, skip_blank)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LinePick", SYLinePick)
