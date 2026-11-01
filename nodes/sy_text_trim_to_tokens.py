"""Text Trim To Tokens SY: cuts a text down to a rough token budget (4 characters per token), keeping the start, end or middle."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

CHARS_PER_TOKEN = 4
KEEP_CHOICES = ("start", "end", "middle")
CUT_CHOICES = ("exact characters", "whole words", "whole tags (commas)")


def estimate_tokens(text):
    """Pure function. Rough count: one token per 4 characters, rounded up."""
    return -(-len(text) // CHARS_PER_TOKEN)


def _snap(text, a, b, cut_at):
    """Takes text[a:b] but moves a ragged edge back to the nearest word or tag border."""
    out = text[a:b]
    if cut_at == CUT_CHOICES[0]:
        return out
    is_border = (lambda c: c.isspace()) if cut_at == CUT_CHOICES[1] else (lambda c: c == ",")
    if b < len(text) and not is_border(text[b - 1]) and not is_border(text[b]):
        idx = max((i for i, c in enumerate(out) if is_border(c)), default=-1)
        if idx >= 0:
            out = out[:idx]
    if a > 0 and out and not is_border(text[a - 1]) and not is_border(text[a]):
        idx = next((i for i, c in enumerate(out) if is_border(c)), -1)
        if idx >= 0:
            out = out[idx + 1:]
    return out.strip() if cut_at == CUT_CHOICES[1] else out.strip(" ,\t\r\n")


def trim_to_tokens(text, max_tokens, keep="start", cut_at=CUT_CHOICES[0]):
    """Pure function. Returns (text, was_trimmed). cut_at can move the cut back to a whole word or a whole tag."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    max_tokens = int(max_tokens)
    if max_tokens < 1:
        raise ValueError("max_tokens must be at least 1, got %d" % max_tokens)
    if keep not in KEEP_CHOICES:
        raise ValueError("keep must be one of: %s (got %r)" % (", ".join(KEEP_CHOICES), keep))
    if cut_at not in CUT_CHOICES:
        raise ValueError("cut_at must be one of: %s (got %r)" % (", ".join(CUT_CHOICES), cut_at))
    budget = max_tokens * CHARS_PER_TOKEN
    if len(text) <= budget:
        return text, False
    if keep == "start":
        a, b = 0, budget
    elif keep == "end":
        a, b = len(text) - budget, len(text)
    else:
        a = (len(text) - budget) // 2
        b = a + budget
    return _snap(text, a, b, cut_at), True


def trim_info(original, result, max_tokens, keep, cut_at, trimmed):
    """Pure function. One plain line: was the text cut and how."""
    if not trimmed:
        return "No cut needed: about %d of %d tokens" % (estimate_tokens(original), int(max_tokens))
    return "Cut from about %d to %d tokens (limit %d), kept the %s, cut at %s" % (
        estimate_tokens(original), estimate_tokens(result), int(max_tokens), keep, cut_at)


class SYTextTrimToTokens:
    DESCRIPTION = ("Cuts a text to a rough token budget, counting 4 characters as 1 token. Keep the start, the end or the middle. "
                   "Can cut at a whole word or a whole comma tag so no word is chopped in half, and the info line says what was cut.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("text", "estimated_tokens", "was_trimmed", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to shorten."}),
                "max_tokens": ("INT", {"default": 256, "min": 1, "max": 1000000, "tooltip": "Token budget. One token is counted as 4 characters."}),
                "keep": (list(KEEP_CHOICES), {"default": "start", "tooltip": "Which part survives when the text is too long."}),
            },
            "optional": {
                "cut_at": (list(CUT_CHOICES), {"default": CUT_CHOICES[0], "tooltip": "Where the cut may fall: anywhere, between words, or between comma tags."}),
            },
        }

    def run(self, text, max_tokens, keep, cut_at=CUT_CHOICES[0]):
        out, trimmed = trim_to_tokens(text, max_tokens, keep, cut_at)
        return (out, estimate_tokens(out), trimmed, trim_info(text, out, max_tokens, keep, cut_at, trimmed))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextTrimToTokens", SYTextTrimToTokens)
NODE_DISPLAY_NAME_MAPPINGS["SYTextTrimToTokens"] = "Text Trim To Tokens SY"
