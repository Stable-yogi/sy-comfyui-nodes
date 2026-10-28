"""Text Number Format SY: turns a number into text with padding, decimals, prefix and suffix."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


class AnyType(str):
    """ComfyUI any-type trick: never reports a type mismatch."""

    def __ne__(self, other):
        return False


ANY = AnyType("*")


def format_number(number, decimals=0, pad_width=0, prefix="", suffix="", thousands=False):
    """Pure function. pad_width zero-pads the whole-number part, so 7 with width 3 gives 007."""
    if isinstance(number, str):
        try:
            number = float(number.strip())
        except ValueError:
            raise ValueError("number %r is not a number: connect a number or type digits" % number)
    try:
        number = float(number)
    except (TypeError, ValueError):
        raise ValueError("number must be a number, got %s" % type(number).__name__)
    if math.isnan(number) or math.isinf(number):
        raise ValueError("number must be a normal number, not nan or infinity")
    decimals = int(decimals)
    pad_width = int(pad_width)
    if not 0 <= decimals <= 10:
        raise ValueError("decimals must be between 0 and 10, got %d" % decimals)
    if not 0 <= pad_width <= 32:
        raise ValueError("pad_width must be between 0 and 32, got %d" % pad_width)
    body = "%.*f" % (decimals, abs(number))
    whole, _, frac = body.partition(".")
    whole = whole.zfill(pad_width)
    if thousands:
        digits = whole.lstrip("0") or "0"
        grouped = "{:,}".format(int(digits))
        whole = grouped if len(digits) >= pad_width else whole
    negative = number < 0 and float(body) != 0
    out = ("-" if negative else "") + whole + (("." + frac) if frac else "")
    return "%s%s%s" % (prefix, out, suffix)


class SYTextNumberFormat:
    DESCRIPTION = "Turns a number into text. Set decimals, zero padding (7 becomes 007), thousands commas, and a prefix and suffix."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "number": ("FLOAT", {"default": 0.0, "min": -1e12, "max": 1e12, "step": 0.01, "tooltip": "The number to turn into text."}),
                "decimals": ("INT", {"default": 0, "min": 0, "max": 10, "tooltip": "How many digits after the decimal point."}),
                "pad_width": ("INT", {"default": 0, "min": 0, "max": 32, "tooltip": "Fill the whole-number part with leading zeros up to this width."}),
                "thousands": ("BOOLEAN", {"default": False, "tooltip": "Put commas between groups of three digits."}),
                "prefix": ("STRING", {"default": "", "tooltip": "Text added before the number."}),
                "suffix": ("STRING", {"default": "", "tooltip": "Text added after the number."}),
            },
            "optional": {
                "number_in": (ANY, {"tooltip": "Connect an INT or FLOAT here to use it instead of the number box."}),
            },
        }

    def run(self, number, decimals=0, pad_width=0, thousands=False, prefix="", suffix="", number_in=None):
        value = number if number_in is None else number_in
        return (format_number(value, decimals, pad_width, prefix, suffix, thousands),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextNumberFormat", SYTextNumberFormat)
NODE_DISPLAY_NAME_MAPPINGS["SYTextNumberFormat"] = "Text Number Format SY"
