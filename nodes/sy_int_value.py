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


def int_info(value):
    """Pure function. Returns (text, info). The info line says which picture-size and video-length rules the number meets."""
    v, _ = int_value(value)
    mults = [m for m in (8, 16, 32, 64) if v % m == 0]
    if mults:
        mtxt = "multiple of " + ", ".join(str(m) for m in mults)
    else:
        mtxt = "not a multiple of 8"
    four = "4n+1 (fits video frame rule)" if v >= 1 and (v - 1) % 4 == 0 else "not 4n+1"
    return str(v), "%d: %s, %s, %s" % (v, "even" if v % 2 == 0 else "odd", mtxt, four)


class SYIntValue:
    DESCRIPTION = "A whole number. Type it once and plug it into as many nodes as you like. Also gives the same number as a decimal, as text, and an info line that tells if it fits size rules (multiple of 8 or 64) and the video frame rule (4n+1)."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "STRING", "STRING")
    RETURN_NAMES = ("int", "float", "text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"value": ("INT", {"default": 0, "min": -LIMIT, "max": LIMIT, "tooltip": "The whole number to send out."})}}

    def run(self, value):
        return int_value(value) + int_info(value)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "IntValue", SYIntValue)
NODE_DISPLAY_NAME_MAPPINGS["SYIntValue"] = "Int Value SY"
