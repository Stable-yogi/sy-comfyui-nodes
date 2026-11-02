"""Cumulative Sum SY: running total (or average, maximum, minimum, difference) of a list of numbers."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("running total", "running average", "running maximum", "running minimum", "difference from previous")


def parse_numbers(text):
    """Pure function. Splits text on commas, semicolons, spaces and line breaks and reads each item as a number.
    A bad item is refused with the item and its position (counting from 1)."""
    if not isinstance(text, str):
        raise ValueError("numbers must be text")
    out = []
    for i, item in enumerate([p for p in re.split(r"[,;\s]+", text) if p != ""], start=1):
        try:
            v = float(item)
        except ValueError:
            raise ValueError("item %d (%r) is not a number: remove it or write it as digits, like 12 or 3.5" % (i, item)) from None
        if v != v or v in (float("inf"), float("-inf")):
            raise ValueError("item %d (%r) is not a normal number: use digits only" % (i, item))
        out.append(v)
    return out


def running(values, mode):
    """Pure function. Returns a list the same length as values. For difference from previous the first
    item is 0 (it has no previous one)."""
    if mode not in MODES:
        raise ValueError("mode must be one of: %s (got %r)" % (", ".join(MODES), mode))
    out = []
    total = 0.0
    for i, v in enumerate(values):
        if mode == "running total":
            total += v
            out.append(total)
        elif mode == "running average":
            total += v
            out.append(total / (i + 1))
        elif mode == "running maximum":
            out.append(v if i == 0 else max(out[-1], v))
        elif mode == "running minimum":
            out.append(v if i == 0 else min(out[-1], v))
        else:
            out.append(0.0 if i == 0 else v - values[i - 1])
    return out


def format_value(v, decimals):
    """Pure function. Rounds to decimals and drops trailing zeros."""
    s = "%.*f" % (decimals, v)
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def cumulative(numbers, mode, separator, decimals):
    """Pure function. Returns (result_text, last, count)."""
    decimals = int(decimals)
    if decimals < 0 or decimals > 10:
        raise ValueError("decimals must be 0 to 10, got %d" % decimals)
    vals = parse_numbers(numbers)
    if not vals:
        if mode not in MODES:
            raise ValueError("mode must be one of: %s (got %r)" % (", ".join(MODES), mode))
        return ("", 0.0, 0)
    res = running(vals, mode)
    return (str(separator).join(format_value(v, decimals) for v in res), float(res[-1]), len(res))


class SYCumulativeSum:
    DESCRIPTION = ("Running total of a list of numbers. Also running average, maximum, minimum, or the "
                   "difference from the previous number. Separate the numbers with commas, spaces or new lines.")
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "FLOAT", "INT")
    RETURN_NAMES = ("result", "last", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "numbers": ("STRING", {"multiline": True, "default": "1, 2, 3, 4", "tooltip": "The numbers, separated by commas, spaces or new lines."}),
                "mode": (list(MODES), {"default": "running total", "tooltip": "What to work out after each number."}),
                "separator": ("STRING", {"default": ", ", "tooltip": "Text put between the numbers in the result."}),
                "decimals": ("INT", {"default": 2, "min": 0, "max": 10, "tooltip": "How many decimals to show in the result text."}),
            }
        }

    def run(self, numbers, mode, separator, decimals):
        return cumulative(numbers, mode, separator, decimals)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CumulativeSum", SYCumulativeSum)
NODE_DISPLAY_NAME_MAPPINGS["SYCumulativeSum"] = "Cumulative Sum SY"
