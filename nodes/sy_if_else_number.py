"""If Else Number SY: a yes/no value chooses between two numbers."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def if_else_number(condition, if_true, if_false):
    """Pure function. Returns (float, int). The int is the nearest whole number, halves go away from 0."""
    if not isinstance(condition, bool):
        raise ValueError("condition must be yes or no (True or False), got %r." % (condition,))
    for name, v in (("if_true", if_true), ("if_false", if_false)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError("%s must be a normal number, got %r." % (name, v))
    chosen = if_true if condition else if_false
    return float(chosen), int(math.floor(abs(chosen) + 0.5)) * (1 if chosen >= 0 else -1)


class SYIfElseNumber:
    DESCRIPTION = "Picks one of two numbers. Yes sends if_true. No sends if_false."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("float", "int")

    @classmethod
    def INPUT_TYPES(cls):
        def num(tip):
            return ("FLOAT", {"default": 0.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": tip})
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True, "tooltip": "Yes sends if_true. No sends if_false."}),
                "if_true": num("The number sent when the condition is yes."),
                "if_false": num("The number sent when the condition is no."),
            }
        }

    def run(self, condition, if_true, if_false):
        return if_else_number(condition, if_true, if_false)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "IfElseNumber", SYIfElseNumber)
NODE_DISPLAY_NAME_MAPPINGS["SYIfElseNumber"] = "If Else Number SY"
