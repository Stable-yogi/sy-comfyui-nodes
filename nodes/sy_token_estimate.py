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


def estimate_info(words, chars, tokens, token_limit=0):
    """Pure function. Returns (over_limit, sentence). Mentions how many 75-token pieces a CLIP text encoder needs."""
    token_limit = int(token_limit)
    chunks = -(-tokens // 75) if tokens else 0
    line = "About %d tokens (%d words, %d characters); a CLIP text encoder reads this in %d piece(s) of 75" % (tokens, words, chars, chunks)
    if token_limit <= 0:
        return False, line
    if tokens > token_limit:
        return True, line + "; OVER your limit of %d by about %d tokens" % (token_limit, tokens - token_limit)
    return False, line + "; within your limit of %d (%d left)" % (token_limit, token_limit - tokens)


class SYTokenEstimate:
    DESCRIPTION = ("Gives a rough word, character and token count. The token number is only an estimate, not what a real tokenizer would say. "
                   "Set a token limit to get a true or false for going over it, and the info line shows how many 75-token pieces a CLIP encoder needs.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("words", "chars", "tokens_estimate", "over_limit", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to measure."})},
            "optional": {"token_limit": ("INT", {"default": 0, "min": 0, "max": 10000000, "tooltip": "Your limit in tokens, for example 77 or 225. 0 means no limit."})},
        }

    def run(self, text, token_limit=0):
        words, chars, tokens = estimate_tokens(text)
        over, info = estimate_info(words, chars, tokens, token_limit)
        return (words, chars, tokens, over, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TokenEstimate", SYTokenEstimate)
NODE_DISPLAY_NAME_MAPPINGS["SYTokenEstimate"] = "Token Estimate SY"
