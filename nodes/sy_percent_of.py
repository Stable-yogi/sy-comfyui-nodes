"""Percent Of SY: three everyday percentage sums in one node."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("percent_of", "what_percent", "change_by_percent")


def percent_calc(mode, a, b):
    """Pure function. Returns (result, info).

    percent_of:        a percent of b
    what_percent:      a is what percent of b
    change_by_percent: a changed up or down by b percent
    """
    a = float(a)
    b = float(b)
    if mode == "percent_of":
        result = a * b / 100.0
        info = "%s%% of %s = %s" % (a, b, result)
    elif mode == "what_percent":
        if b == 0:
            raise ValueError("b must not be 0 in what_percent mode: you cannot ask what percent of zero")
        result = a / b * 100.0
        info = "%s is %s%% of %s" % (a, result, b)
    elif mode == "change_by_percent":
        result = a * (100.0 + b) / 100.0
        info = "%s changed by %s%% = %s" % (a, b, result)
    else:
        raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))
    return result, info


class SYPercentOf:
    DESCRIPTION = "Does percentage sums. Find a percent of a number, find what percent one number is of another, or raise or lower a number by a percent."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "STRING")
    RETURN_NAMES = ("result", "info")

    @classmethod
    def INPUT_TYPES(cls):
        big = 1.0e9
        return {
            "required": {
                "mode": (list(MODES), {"default": "percent_of", "tooltip": "percent_of: a% of b. what_percent: a is what % of b. change_by_percent: a changed by b%."}),
                "a": ("FLOAT", {"default": 10.0, "min": -big, "max": big, "step": 0.01, "tooltip": "The first number. See the mode for how it is used."}),
                "b": ("FLOAT", {"default": 200.0, "min": -big, "max": big, "step": 0.01, "tooltip": "The second number. See the mode for how it is used."}),
            }
        }

    def run(self, mode, a, b):
        return percent_calc(mode, a, b)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PercentOf", SYPercentOf)
