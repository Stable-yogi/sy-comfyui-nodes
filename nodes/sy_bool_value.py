"""Bool Value SY: a yes/no switch you set once and use in many places."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def bool_value(value):
    """Pure function. Returns (bool, int) where the int is 1 for yes and 0 for no."""
    if not isinstance(value, bool):
        raise ValueError("Bool Value needs yes or no (True or False), got %r." % (value,))
    return value, 1 if value else 0


class SYBoolValue:
    DESCRIPTION = "A yes/no switch. Set it once and plug it into as many nodes as you like. Also gives 1 for yes and 0 for no."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "INT")
    RETURN_NAMES = ("boolean", "int")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"value": ("BOOLEAN", {"default": False, "label_on": "yes", "label_off": "no", "tooltip": "The yes/no value to send out."})}}

    def run(self, value):
        return bool_value(value)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BoolValue", SYBoolValue)
NODE_DISPLAY_NAME_MAPPINGS["SYBoolValue"] = "Bool Value SY"
