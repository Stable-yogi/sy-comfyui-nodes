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


class SYFloatValue:
    DESCRIPTION = "A decimal number. Type it once and plug it into as many nodes as you like. Also gives the nearest whole number."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("float", "int")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"value": ("FLOAT", {"default": 0.0, "min": -LIMIT, "max": LIMIT, "step": 0.01, "tooltip": "The decimal number to send out."})}}

    def run(self, value):
        return float_value(value)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "FloatValue", SYFloatValue)
NODE_DISPLAY_NAME_MAPPINGS["SYFloatValue"] = "Float Value SY"
