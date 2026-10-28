"""Prompt Weight Wrap SY: wraps a prompt in a weight or in brackets."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

STYLES = ["weight (text:1.2)", "round ( )", "double round (( ))", "square [ ]", "curly { }"]


def wrap_prompt(text, style="weight (text:1.2)", weight=1.2):
    """Pure function. Empty text stays empty. A weight of exactly 1 leaves the text as it is."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    if style not in STYLES:
        raise ValueError("style must be one of: %s" % ", ".join(STYLES))
    text = text.strip()
    if text == "":
        return ""
    if style == STYLES[0]:
        weight = float(weight)
        if weight != weight or weight < 0 or weight > 10:
            raise ValueError("weight must be between 0 and 10, got %s" % weight)
        if weight == 1.0:
            return text
        return "(%s:%s)" % (text, ("%.3f" % weight).rstrip("0").rstrip("."))
    if style == STYLES[1]:
        return "(%s)" % text
    if style == STYLES[2]:
        return "((%s))" % text
    if style == STYLES[3]:
        return "[%s]" % text
    return "{%s}" % text


class SYPromptWeightWrap:
    DESCRIPTION = "Wraps a prompt as (text:1.2) with a weight, or in round, square or curly brackets. Empty text stays empty."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The prompt part to wrap."}),
                "style": (STYLES, {"default": STYLES[0], "tooltip": "How to wrap: with a weight number or with a bracket type."}),
                "weight": ("FLOAT", {"default": 1.2, "min": 0.0, "max": 10.0, "step": 0.05, "tooltip": "Strength for the weight style. 1 means no change."}),
            }
        }

    def run(self, text, style=STYLES[0], weight=1.2):
        return (wrap_prompt(text, style, weight),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptWeightWrap", SYPromptWeightWrap)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptWeightWrap"] = "Prompt Weight Wrap SY"
