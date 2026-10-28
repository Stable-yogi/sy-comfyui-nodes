"""If Else Text SY: a yes/no value chooses between two pieces of text."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def if_else_text(condition, if_true, if_false):
    """Pure function. Yes gives if_true, no gives if_false."""
    if not isinstance(condition, bool):
        raise ValueError("condition must be yes or no (True or False), got %r." % (condition,))
    for name, v in (("if_true", if_true), ("if_false", if_false)):
        if not isinstance(v, str):
            raise ValueError("%s must be text, got %r." % (name, v))
    return if_true if condition else if_false


class SYIfElseText:
    DESCRIPTION = "Picks one of two texts. Yes sends if_true. No sends if_false."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True, "tooltip": "Yes sends if_true. No sends if_false."}),
                "if_true": ("STRING", {"default": "", "multiline": True, "tooltip": "The text sent when the condition is yes."}),
                "if_false": ("STRING", {"default": "", "multiline": True, "tooltip": "The text sent when the condition is no."}),
            }
        }

    def run(self, condition, if_true, if_false):
        return (if_else_text(condition, if_true, if_false),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "IfElseText", SYIfElseText)
NODE_DISPLAY_NAME_MAPPINGS["SYIfElseText"] = "If Else Text SY"
