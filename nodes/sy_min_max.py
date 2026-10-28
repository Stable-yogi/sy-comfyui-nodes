"""Min Max SY: gives the smaller and the bigger of two numbers."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def min_max(a, b):
    """Pure function. Returns (smaller, bigger) as floats."""
    for name, v in (("a", a), ("b", b)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError("%s must be a normal number, got %r." % (name, v))
    return float(min(a, b)), float(max(a, b))


class SYMinMax:
    DESCRIPTION = "Takes two numbers and gives the smaller one and the bigger one."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "FLOAT")
    RETURN_NAMES = ("min", "max")

    @classmethod
    def INPUT_TYPES(cls):
        def num(tip):
            return ("FLOAT", {"default": 0.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": tip})
        return {"required": {"a": num("The first number."), "b": num("The second number.")}}

    def run(self, a, b):
        return min_max(a, b)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MinMax", SYMinMax)
NODE_DISPLAY_NAME_MAPPINGS["SYMinMax"] = "Min Max SY"
