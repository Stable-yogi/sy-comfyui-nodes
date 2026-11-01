"""If Else Number SY: a yes/no value chooses between two numbers."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


ROUNDING = ("nearest", "floor", "ceil", "toward zero")


def to_whole(value, rounding="nearest"):
    """Pure function. Float to whole number. nearest: halves go away from 0. floor: down. ceil: up. toward zero: cut the decimals."""
    if rounding == "nearest":
        return int(math.floor(abs(value) + 0.5)) * (1 if value >= 0 else -1)
    if rounding == "floor":
        return int(math.floor(value))
    if rounding == "ceil":
        return int(math.ceil(value))
    if rounding == "toward zero":
        return int(value)
    raise ValueError("rounding must be one of %s, got %r." % (", ".join(ROUNDING), rounding))


def if_else_info(condition, chosen, whole, rounding="nearest"):
    """Pure function. A plain line saying which side was taken."""
    side = "yes: took if_true" if condition else "no: took if_false"
    text = "%s = %g" % (side, chosen)
    if float(whole) != float(chosen):
        text += ", whole number %d (%s)" % (whole, rounding)
    return text


def if_else_number(condition, if_true, if_false, rounding="nearest"):
    """Pure function. Returns (float, int). The int is the nearest whole number by default, halves go away from 0."""
    if not isinstance(condition, bool):
        raise ValueError("condition must be yes or no (True or False), got %r." % (condition,))
    for name, v in (("if_true", if_true), ("if_false", if_false)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError("%s must be a normal number, got %r." % (name, v))
    chosen = if_true if condition else if_false
    return float(chosen), to_whole(chosen, rounding)


class SYIfElseNumber:
    DESCRIPTION = "Picks one of two numbers. Yes sends if_true. No sends if_false. You get it as a decimal and as a whole number (you choose how it rounds), plus a plain info line."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "INT", "STRING")
    RETURN_NAMES = ("float", "int", "info")

    @classmethod
    def INPUT_TYPES(cls):
        def num(tip):
            return ("FLOAT", {"default": 0.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": tip})
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True, "tooltip": "Yes sends if_true. No sends if_false."}),
                "if_true": num("The number sent when the condition is yes."),
                "if_false": num("The number sent when the condition is no."),
            },
            "optional": {
                "rounding": (list(ROUNDING), {"default": "nearest", "tooltip": "How the whole number is made: 2.5 gives 3 (nearest), 2 (floor), 3 (ceil) or 2 (toward zero)."}),
            },
        }

    def run(self, condition, if_true, if_false, rounding="nearest"):
        as_float, as_int = if_else_number(condition, if_true, if_false, rounding)
        return (as_float, as_int, if_else_info(condition, as_float, as_int, rounding))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "IfElseNumber", SYIfElseNumber)
NODE_DISPLAY_NAME_MAPPINGS["SYIfElseNumber"] = "If Else Number SY"
