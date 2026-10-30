"""Line Numbers SY: puts a number in front of every line of a text."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def number_lines(lines, start, separator, pad_zeros, skip_empty):
    """Pure function. Returns (new_lines, count). An empty line (nothing but spaces) is skipped when skip_empty is on."""
    if not -1000000 <= start <= 1000000:
        raise ValueError("start must be between -1000000 and 1000000, got %s" % start)
    numbered = [i for i, line in enumerate(lines) if not (skip_empty and line.strip() == "")]
    numbers = {idx: start + n for n, idx in enumerate(numbered)}
    width = max((len(str(v)) for v in numbers.values()), default=0) if pad_zeros else 0
    out = []
    for i, line in enumerate(lines):
        if i in numbers:
            out.append(str(numbers[i]).zfill(width) + separator + line)
        else:
            out.append(line)
    return out, len(numbered)


class SYLineNumbers:
    DESCRIPTION = "Puts a number in front of every line of a text. Can skip empty lines and pad the numbers with zeros."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("text", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to number, one number per line."}),
                "start": ("INT", {"default": 1, "min": -1000000, "max": 1000000, "tooltip": "The number given to the first line."}),
                "separator": ("STRING", {"default": ". ", "tooltip": "Text placed between the number and the line."}),
                "pad_zeros": ("BOOLEAN", {"default": False, "tooltip": "On: fill numbers with leading zeros so they all have the same width."}),
                "skip_empty": ("BOOLEAN", {"default": False, "tooltip": "On: empty lines get no number and are not counted."}),
            }
        }

    def run(self, text, start, separator, pad_zeros, skip_empty):
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        out, count = number_lines(lines, start, separator, pad_zeros, skip_empty)
        return ("\n".join(out), count)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LineNumbers", SYLineNumbers)
NODE_DISPLAY_NAME_MAPPINGS["SYLineNumbers"] = "Line Numbers SY"
