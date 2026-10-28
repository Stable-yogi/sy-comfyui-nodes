"""Text Trim To Tokens SY: cuts a text down to a rough token budget (4 characters per token), keeping the start, end or middle."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

CHARS_PER_TOKEN = 4
KEEP_CHOICES = ("start", "end", "middle")


def estimate_tokens(text):
    """Pure function. Rough count: one token per 4 characters, rounded up."""
    return -(-len(text) // CHARS_PER_TOKEN)


def trim_to_tokens(text, max_tokens, keep="start"):
    """Pure function. Returns (text, was_trimmed)."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    max_tokens = int(max_tokens)
    if max_tokens < 1:
        raise ValueError("max_tokens must be at least 1, got %d" % max_tokens)
    if keep not in KEEP_CHOICES:
        raise ValueError("keep must be one of: %s (got %r)" % (", ".join(KEEP_CHOICES), keep))
    budget = max_tokens * CHARS_PER_TOKEN
    if len(text) <= budget:
        return text, False
    if keep == "start":
        out = text[:budget]
    elif keep == "end":
        out = text[len(text) - budget:]
    else:
        first = (len(text) - budget) // 2
        out = text[first:first + budget]
    return out, True


class SYTextTrimToTokens:
    DESCRIPTION = "Cuts a text to a rough token budget, counting 4 characters as 1 token. Keep the start, the end or the middle."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "BOOLEAN")
    RETURN_NAMES = ("text", "estimated_tokens", "was_trimmed")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to shorten."}),
                "max_tokens": ("INT", {"default": 256, "min": 1, "max": 1000000, "tooltip": "Token budget. One token is counted as 4 characters."}),
                "keep": (list(KEEP_CHOICES), {"default": "start", "tooltip": "Which part survives when the text is too long."}),
            }
        }

    def run(self, text, max_tokens, keep):
        out, trimmed = trim_to_tokens(text, max_tokens, keep)
        return (out, estimate_tokens(out), trimmed)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextTrimToTokens", SYTextTrimToTokens)
NODE_DISPLAY_NAME_MAPPINGS["SYTextTrimToTokens"] = "Text Trim To Tokens SY"
