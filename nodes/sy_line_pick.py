"""Line Pick SY: takes one line out of a multi-line text by its number."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


OUT_OF_RANGE = ("error", "wrap around", "clamp to ends")


def line_pick_ex(text, index, skip_blank, out_of_range="error", strip=False):
    """Pure function. Returns (line, total, position, note). position counts from 0. note is '', 'wrapped' or 'clamped'."""
    if out_of_range not in OUT_OF_RANGE:
        raise ValueError("out_of_range must be one of: %s, got %r" % (", ".join(OUT_OF_RANGE), out_of_range))
    lines = str(text).splitlines()
    if skip_blank:
        lines = [x for x in lines if x.strip()]
    total = len(lines)
    index = int(index)
    if total == 0:
        raise ValueError("text has no lines to pick from")
    note = ""
    if index >= total or index < -total:
        if out_of_range == "error":
            raise ValueError("index %d is out of range: the text has %d lines (use %d to %d)" % (index, total, -total, total - 1))
        if out_of_range == "wrap around":
            index = index % total
            note = "wrapped"
        else:
            index = total - 1 if index > 0 else 0
            note = "clamped"
    position = index % total
    line = lines[position]
    return (line.strip() if strip else line), total, position, note


def line_pick(text, index, skip_blank, out_of_range="error", strip=False):
    """Pure function. Returns (line, total). A negative index counts from the end."""
    line, total, _, _ = line_pick_ex(text, index, skip_blank, out_of_range, strip)
    return line, total


class SYLinePick:
    DESCRIPTION = ("Takes one line from a text. Count from the top with 0, 1, 2 or from the bottom with -1, -2. A number that is too big "
                   "can wrap round to the start (handy with a counter) or stick to the last line instead of stopping, and an info line "
                   "says which line was taken.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("line", "total_lines", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text with several lines."}),
                "index": ("INT", {"default": 0, "min": -100000, "max": 100000, "tooltip": "Line to take, counting from 0. Negative counts from the end."}),
                "skip_blank": ("BOOLEAN", {"default": True, "tooltip": "Ignore empty lines when counting."}),
            },
            "optional": {
                "out_of_range": (list(OUT_OF_RANGE), {"default": "error", "tooltip": "If the index is past the last line: stop with a message, wrap round to the start, or use the nearest end."}),
                "strip": ("BOOLEAN", {"default": False, "tooltip": "On: remove spaces around the picked line."}),
            },
        }

    def run(self, text, index, skip_blank, out_of_range="error", strip=False):
        line, total, position, note = line_pick_ex(text, index, skip_blank, out_of_range, strip)
        info = "Picked line %d of %d" % (position + 1, total)
        if note == "wrapped":
            info += " (index %d wrapped round)" % index
        elif note == "clamped":
            info += " (index %d was past the end)" % index
        return line, total, info + "."


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LinePick", SYLinePick)
