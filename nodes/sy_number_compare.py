"""Number Compare SY: compares two numbers and says yes or no."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

OPERATORS = ("==", "!=", "<", "<=", ">", ">=")


def number_compare(a, b, operator, tolerance=0.0):
    """Pure function. Returns True or False. tolerance counts two numbers as equal when they differ by no more than it."""
    for name, v in (("a", a), ("b", b)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError("%s must be a normal number, got %r." % (name, v))
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be 0 or more, got %r. Use something like 0.0001." % (tolerance,))
    same = abs(a - b) <= tolerance
    if operator == "==":
        return same
    if operator == "!=":
        return not same
    if operator == "<":
        return a < b and not same
    if operator == "<=":
        return a < b or same
    if operator == ">":
        return a > b and not same
    if operator == ">=":
        return a > b or same
    raise ValueError("operator must be one of %s, got %r." % (" ".join(OPERATORS), operator))


def compare_info(a, b, operator, tolerance=0.0):
    """Pure function. Returns (difference, info): a minus b and one plain sentence."""
    result = number_compare(a, b, operator, tolerance)
    text = "%g %s %g is %s (a minus b = %g)" % (a, operator, b, "yes" if result else "no", a - b)
    if tolerance:
        text += ", numbers within %g count as equal" % tolerance
    return a - b, text


class SYNumberCompare:
    DESCRIPTION = "Compares number a with number b and gives yes or no. Use it to drive a switch. The optional tolerance treats nearly equal decimals as equal. Also gives a plain info line and the difference a minus b."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING", "FLOAT")
    RETURN_NAMES = ("result", "info", "difference")

    @classmethod
    def INPUT_TYPES(cls):
        def num(tip):
            return ("FLOAT", {"default": 0.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": tip})
        return {
            "required": {
                "a": num("The number on the left."),
                "operator": (list(OPERATORS), {"default": "==", "tooltip": "How to compare: equal, not equal, smaller, bigger and so on."}),
                "b": num("The number on the right."),
            },
            "optional": {
                "tolerance": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1e15, "step": 0.0001, "tooltip": "Numbers this close count as equal. Fixes 0.1+0.2 vs 0.3. Example: 0.0001."}),
            },
        }

    def run(self, a, operator, b, tolerance=0.0):
        diff, info = compare_info(a, b, operator, tolerance)
        return (number_compare(a, b, operator, tolerance), info, diff)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "NumberCompare", SYNumberCompare)
NODE_DISPLAY_NAME_MAPPINGS["SYNumberCompare"] = "Number Compare SY"
