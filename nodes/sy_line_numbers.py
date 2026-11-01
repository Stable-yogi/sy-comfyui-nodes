"""Line Numbers SY: puts a number in front of every line of a text."""
import re

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


MODES = ("add numbers", "remove numbers")
_ANY_NUMBER = re.compile(r"^\s*-?\d+\s*[.):\-]?\s")


def strip_numbers(lines, separator=". "):
    """Pure function. Takes a leading number off every line (the number plus your separator, or a plain '3.' / '3)' / '3 '). Returns (new_lines, changed_count)."""
    out = []
    changed = 0
    exact = re.compile(r"^-?\d+" + re.escape(separator)) if separator else None
    for line in lines:
        m = exact.match(line) if exact else None
        if not m:
            m = _ANY_NUMBER.match(line)
        if m:
            out.append(line[m.end():])
            changed += 1
        else:
            out.append(line)
    return out, changed


class SYLineNumbers:
    DESCRIPTION = ("Puts a number in front of every line of a text. Can skip empty lines and pad the numbers with zeros. The other mode "
                   "takes numbers off a numbered list again. An info line says what was done.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("text", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to number, one number per line."}),
                "start": ("INT", {"default": 1, "min": -1000000, "max": 1000000, "tooltip": "The number given to the first line."}),
                "separator": ("STRING", {"default": ". ", "tooltip": "Text placed between the number and the line."}),
                "pad_zeros": ("BOOLEAN", {"default": False, "tooltip": "On: fill numbers with leading zeros so they all have the same width."}),
                "skip_empty": ("BOOLEAN", {"default": False, "tooltip": "On: empty lines get no number and are not counted."}),
            },
            "optional": {
                "mode": (list(MODES), {"default": "add numbers", "tooltip": "add numbers: number the lines. remove numbers: take the numbers off a list like 1. a / 2. b."}),
            },
        }

    def run(self, text, start, separator, pad_zeros, skip_empty, mode="add numbers"):
        if mode not in MODES:
            raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if mode == MODES[1]:
            out, count = strip_numbers(lines, separator)
            return ("\n".join(out), count, "Removed the number from %d of %d line%s." % (count, len(lines), "" if len(lines) == 1 else "s"))
        out, count = number_lines(lines, start, separator, pad_zeros, skip_empty)
        info = "Numbered %d line%s" % (count, "" if count == 1 else "s")
        info += ", starting at %d." % start if count else ": nothing to number."
        return ("\n".join(out), count, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LineNumbers", SYLineNumbers)
NODE_DISPLAY_NAME_MAPPINGS["SYLineNumbers"] = "Line Numbers SY"
