"""Number Compare SY: compares two numbers and says yes or no."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

OPERATORS = ("==", "!=", "<", "<=", ">", ">=")


def number_compare(a, b, operator):
    """Pure function. Returns True or False."""
    for name, v in (("a", a), ("b", b)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError("%s must be a normal number, got %r." % (name, v))
    if operator == "==":
        return a == b
    if operator == "!=":
        return a != b
    if operator == "<":
        return a < b
    if operator == "<=":
        return a <= b
    if operator == ">":
        return a > b
    if operator == ">=":
        return a >= b
    raise ValueError("operator must be one of %s, got %r." % (" ".join(OPERATORS), operator))


class SYNumberCompare:
    DESCRIPTION = "Compares number a with number b and gives yes or no. Use it to drive a switch."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("result",)

    @classmethod
    def INPUT_TYPES(cls):
        def num(tip):
            return ("FLOAT", {"default": 0.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": tip})
        return {
            "required": {
                "a": num("The number on the left."),
                "operator": (list(OPERATORS), {"default": "==", "tooltip": "How to compare: equal, not equal, smaller, bigger and so on."}),
                "b": num("The number on the right."),
            }
        }

    def run(self, a, operator, b):
        return (number_compare(a, b, operator),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "NumberCompare", SYNumberCompare)
NODE_DISPLAY_NAME_MAPPINGS["SYNumberCompare"] = "Number Compare SY"
