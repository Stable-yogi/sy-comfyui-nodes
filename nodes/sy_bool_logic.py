"""Bool Logic SY: and, or, xor and not on yes/no values."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

OPERATIONS = ("and", "or", "xor", "not")


def bool_logic(a, b, operation):
    """Pure function. 'not' only looks at a."""
    for name, v in (("a", a), ("b", b)):
        if not isinstance(v, bool):
            raise ValueError("%s must be yes or no (True or False), got %r." % (name, v))
    if operation == "and":
        return a and b
    if operation == "or":
        return a or b
    if operation == "xor":
        return a != b
    if operation == "not":
        return not a
    raise ValueError("operation must be one of %s, got %r." % (", ".join(OPERATIONS), operation))


class SYBoolLogic:
    DESCRIPTION = "Combines two yes/no values with and, or, xor. The not choice flips a and ignores b."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("result",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "a": ("BOOLEAN", {"default": False, "tooltip": "The first yes/no value."}),
                "b": ("BOOLEAN", {"default": False, "tooltip": "The second yes/no value. Not used by not."}),
                "operation": (list(OPERATIONS), {"default": "and", "tooltip": "and: both yes. or: at least one yes. xor: exactly one yes. not: flip a."}),
            }
        }

    def run(self, a, b, operation):
        return (bool_logic(a, b, operation),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BoolLogic", SYBoolLogic)
NODE_DISPLAY_NAME_MAPPINGS["SYBoolLogic"] = "Bool Logic SY"
