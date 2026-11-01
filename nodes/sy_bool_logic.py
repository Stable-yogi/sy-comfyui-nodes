"""Bool Logic SY: and, or, xor and not on yes/no values."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

OPERATIONS = ("and", "or", "xor", "not", "nand", "nor", "xnor")
WORD = {True: "yes", False: "no"}


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
    if operation == "nand":
        return not (a and b)
    if operation == "nor":
        return not (a or b)
    if operation == "xnor":
        return a == b
    raise ValueError("operation must be one of %s, got %r." % (", ".join(OPERATIONS), operation))


def bool_logic_info(a, b, operation, result):
    """Pure function. One plain line: what went in and what came out."""
    if operation == "not":
        return "not %s -> %s" % (WORD[a], WORD[result])
    return "%s %s %s -> %s" % (WORD[a], operation, WORD[b], WORD[result])


class SYBoolLogic:
    DESCRIPTION = "Combines two yes/no values with and, or, xor, nand, nor or xnor. The not choice flips a and ignores b. The info line shows what went in."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("BOOLEAN", "STRING")
    RETURN_NAMES = ("result", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "a": ("BOOLEAN", {"default": False, "tooltip": "The first yes/no value."}),
                "b": ("BOOLEAN", {"default": False, "tooltip": "The second yes/no value. Not used by not."}),
                "operation": (list(OPERATIONS), {"default": "and", "tooltip": "and: both yes. or: one or more. xor: exactly one. not: flip a. nand/nor/xnor: the opposite of and/or/xor."}),
            }
        }

    def run(self, a, b, operation):
        result = bool_logic(a, b, operation)
        return (result, bool_logic_info(a, b, operation, result))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "BoolLogic", SYBoolLogic)
NODE_DISPLAY_NAME_MAPPINGS["SYBoolLogic"] = "Bool Logic SY"
