"""Token Estimate SY: rough count of words, characters and tokens in a text."""
import math
import re

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def estimate_tokens(text):
    """Pure function. Returns (words, chars, tokens). Tokens is a rough guess, not an exact count."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    chars = len(text)
    words = len(re.findall(r"\S+", text))
    if chars == 0:
        return (0, 0, 0)
    tokens = int(math.ceil((chars / 4.0 + words * 1.3) / 2.0))
    return (words, chars, tokens)


class SYTokenEstimate:
    DESCRIPTION = "Gives a rough word, character and token count. The token number is only an estimate, not what a real tokenizer would say."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("words", "chars", "tokens_estimate")

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to measure."})}}

    def run(self, text):
        return estimate_tokens(text)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TokenEstimate", SYTokenEstimate)
NODE_DISPLAY_NAME_MAPPINGS["SYTokenEstimate"] = "Token Estimate SY"
