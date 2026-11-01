"""Float Value SY: a decimal number you type once and use in many places."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

LIMIT = 1e15


def float_value(value):
    """Pure function. Returns (float, int). The int is the nearest whole number, halves go away from 0."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Float Value needs a normal number, got %r. Type a number like 1.5." % (value,))
    if abs(value) > LIMIT:
        raise ValueError("The number %r is too big. Stay between -%g and %g." % (value, LIMIT, LIMIT))
    rounded = int(math.floor(abs(value) + 0.5)) * (1 if value >= 0 else -1)
    return float(value), rounded


def float_info(value):
    """Pure function. Returns (text, info). text has no trailing zeros; info shows the whole-number choices."""
    v, nearest = float_value(value)
    text = ("%.10g" % v)
    if "e" in text:
        text = repr(v)
    return text, "%s: nearest whole %d, rounded down %d, rounded up %d" % (text, nearest, math.floor(v), math.ceil(v))


class SYFloatValue:
    DESCRIPTION = "A decimal number. Type it once and plug it into as many nodes as you like. Also gives the nearest whole number, the number as clean text, and an info line with the round-down and round-up choices."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "INT", "STRING", "STRING")
    RETURN_NAMES = ("float", "int", "text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"value": ("FLOAT", {"default": 0.0, "min": -LIMIT, "max": LIMIT, "step": 0.01, "tooltip": "The decimal number to send out."})}}

    def run(self, value):
        return float_value(value) + float_info(value)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FloatValue", SYFloatValue)
NODE_DISPLAY_NAME_MAPPINGS["SYFloatValue"] = "Float Value SY"
