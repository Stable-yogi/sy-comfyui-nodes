"""If Else Text SY: a yes/no value chooses between two pieces of text."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def if_else_text(condition, if_true, if_false, fallback_when_empty=False):
    """Pure function. Yes gives if_true, no gives if_false.
    With fallback_when_empty on, a chosen text that is empty (or only spaces) is replaced by the other text."""
    if not isinstance(condition, bool):
        raise ValueError("condition must be yes or no (True or False), got %r." % (condition,))
    for name, v in (("if_true", if_true), ("if_false", if_false)):
        if not isinstance(v, str):
            raise ValueError("%s must be text, got %r." % (name, v))
    chosen, other = (if_true, if_false) if condition else (if_false, if_true)
    if fallback_when_empty and not chosen.strip():
        return other
    return chosen


def if_else_text_info(condition, if_true, if_false, fallback_when_empty=False):
    """Pure function. A plain line saying which text was sent."""
    result = if_else_text(condition, if_true, if_false, fallback_when_empty)
    side = "if_true" if condition else "if_false"
    if fallback_when_empty and result is not (if_true if condition else if_false):
        side = "if_false" if condition else "if_true"
        return "Took %s because %s was empty (%d character%s)." % (side, "if_true" if condition else "if_false", len(result), "" if len(result) == 1 else "s")
    return "Condition is %s: took %s (%d character%s)." % ("yes" if condition else "no", side, len(result), "" if len(result) == 1 else "s")


class SYIfElseText:
    DESCRIPTION = "Picks one of two texts. Yes sends if_true. No sends if_false. Can use the other text when the chosen one is empty, and tells you which one it sent."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True, "tooltip": "Yes sends if_true. No sends if_false."}),
                "if_true": ("STRING", {"default": "", "multiline": True, "tooltip": "The text sent when the condition is yes."}),
                "if_false": ("STRING", {"default": "", "multiline": True, "tooltip": "The text sent when the condition is no."}),
            },
            "optional": {
                "fallback_when_empty": ("BOOLEAN", {"default": False, "tooltip": "On sends the other text when the chosen one is empty or only spaces."}),
            },
        }

    def run(self, condition, if_true, if_false, fallback_when_empty=False):
        return (if_else_text(condition, if_true, if_false, fallback_when_empty),
                if_else_text_info(condition, if_true, if_false, fallback_when_empty))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "IfElseText", SYIfElseText)
NODE_DISPLAY_NAME_MAPPINGS["SYIfElseText"] = "If Else Text SY"
