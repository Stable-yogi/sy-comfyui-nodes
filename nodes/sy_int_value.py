"""Int Value SY: a whole number you type once and use in many places."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

LIMIT = 2 ** 53 - 1


def int_value(value):
    """Pure function. Returns (int, float) of a whole number. Refuses anything that is not a whole number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value != int(value):
        raise ValueError("Int Value needs a whole number, got %r. Type a number like 5." % (value,))
    value = int(value)
    if abs(value) > LIMIT:
        raise ValueError("The number %d is too big. Stay between -%d and %d." % (value, LIMIT, LIMIT))
    return value, float(value)


class SYIntValue:
    DESCRIPTION = "A whole number. Type it once and plug it into as many nodes as you like. Also gives the same number as a decimal."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("int", "float")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"value": ("INT", {"default": 0, "min": -LIMIT, "max": LIMIT, "tooltip": "The whole number to send out."})}}

    def run(self, value):
        return int_value(value)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "IntValue", SYIntValue)
NODE_DISPLAY_NAME_MAPPINGS["SYIntValue"] = "Int Value SY"
