"""Text Extract Numbers SY: pulls the numbers out of a text."""
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

KINDS = ("all numbers", "whole numbers only", "decimals only")
THOUSANDS = ("ignore", "commas are thousands separators")
PICKS = ("all", "first", "last", "largest", "smallest")

# A number is: digits with comma groups of exactly three, or plain digits, with an optional decimal part;
# or a bare decimal like .5 . A trailing dot ("3.") is not part of the number.
_NUM_COMMA = re.compile(r"(?<![A-Za-z0-9])-(?=[\d.])|(\d{1,3}(?:,\d{3})+(?!\d)(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)")
_NUM_PLAIN = re.compile(r"(?<![A-Za-z0-9])-(?=[\d.])|(\d+(?:\.\d+)?|\.\d+)")


def find_numbers(text, kind="all numbers", allow_negative=True, thousands="commas are thousands separators"):
    """Pure function. Returns the numbers in the order they appear (int for whole tokens, float for decimals).
    Notes: 1e3 is NOT one number, it is read as 1 and then 3. Numbers inside words such as abc123 are found.
    A minus sign counts only when it does not directly follow a letter or digit, so 2026-01-31 gives 2026, 1, 31."""
    if not isinstance(text, str):
        raise ValueError("text must be text")
    if kind not in KINDS:
        raise ValueError("kind must be one of: %s (got %r)" % (", ".join(KINDS), kind))
    if thousands not in THOUSANDS:
        raise ValueError("thousands must be one of: %s (got %r)" % (", ".join(THOUSANDS), thousands))
    pat = _NUM_COMMA if thousands == THOUSANDS[1] else _NUM_PLAIN
    out = []
    pending_minus_end = -1
    for mt in pat.finditer(text):
        if mt.group(1) is None:        # a minus sign that may belong to the next number
            pending_minus_end = mt.end()
            continue
        token = mt.group(1).replace(",", "")
        negative = allow_negative and pending_minus_end == mt.start()
        is_decimal = "." in token
        if kind == "whole numbers only" and is_decimal:
            continue
        if kind == "decimals only" and not is_decimal:
            continue
        value = float(token) if is_decimal else int(token)
        out.append(-value if negative else value)
    return out


def pick_numbers(values, pick="all"):
    """Pure function. Narrows the list: all, first, last, largest or smallest."""
    if pick not in PICKS:
        raise ValueError("pick must be one of: %s (got %r)" % (", ".join(PICKS), pick))
    if not values or pick == "all":
        return list(values)
    if pick == "first":
        return [values[0]]
    if pick == "last":
        return [values[-1]]
    if pick == "largest":
        return [max(values)]
    return [min(values)]


def format_number(v):
    """Pure function. Whole numbers without a dot, decimals as short as they can be."""
    if isinstance(v, int):
        return str(v)
    return repr(v)


def extract(text, kind, allow_negative, thousands, pick, separator):
    """Pure function. Returns (numbers_text, count, total, first)."""
    vals = pick_numbers(find_numbers(text, kind, allow_negative, thousands), pick)
    if not vals:
        return ("", 0, 0.0, 0.0)
    return (str(separator).join(format_number(v) for v in vals), len(vals), float(sum(vals)), float(vals[0]))


class SYTextExtractNumbers:
    DESCRIPTION = ("Pulls the numbers out of a text. Handles 1,234.5 and -7. Reads 1e3 as 1 and 3, and finds "
                   "numbers inside words like abc123. No numbers found gives empty text and count 0.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("numbers", "count", "total", "first")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to search for numbers."}),
                "kind": (list(KINDS), {"default": "all numbers", "tooltip": "Which numbers to keep: all, only whole numbers, or only numbers with a decimal point."}),
                "allow_negative": ("BOOLEAN", {"default": True, "tooltip": "On: a minus sign in front of a number makes it negative. Off: the minus is ignored."}),
                "thousands": (list(THOUSANDS), {"default": "commas are thousands separators", "tooltip": "Whether 1,234 is one number or two (1 and 234)."}),
                "pick": (list(PICKS), {"default": "all", "tooltip": "Keep all numbers, or only the first, last, largest or smallest one."}),
                "separator": ("STRING", {"default": ", ", "tooltip": "Text put between the numbers in the output."}),
            }
        }

    def run(self, text, kind, allow_negative, thousands, pick, separator):
        return extract(text, kind, allow_negative, thousands, pick, separator)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextExtractNumbers", SYTextExtractNumbers)
NODE_DISPLAY_NAME_MAPPINGS["SYTextExtractNumbers"] = "Text Extract Numbers SY"
