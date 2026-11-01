"""Text Stats SY: counts characters, words, lines and guesses the token count of a text."""

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def text_stats(text):
    """Pure function. Returns (chars, words, lines, tokens). Tokens are chars / 4 rounded up."""
    text = str(text)
    chars = len(text)
    words = len(text.split())
    lines = len(text.splitlines())
    tokens = (chars + 3) // 4
    return chars, words, lines, tokens


def limit_info(tokens, token_limit):
    """Pure function. Compares the token guess with a limit. 0 means no limit. Returns (over_limit, sentence)."""
    token_limit = int(token_limit)
    if token_limit <= 0:
        return False, "No token limit set"
    if tokens > token_limit:
        return True, "OVER the limit by %d tokens (%d of %d): shorten the text" % (tokens - token_limit, tokens, token_limit)
    return False, "Within the limit: %d of %d tokens (%d left)" % (tokens, token_limit, token_limit - tokens)


def summary_text(stats):
    chars, words, lines, tokens = stats
    return "%d chars, %d words, %d lines, about %d tokens" % (chars, words, lines, tokens)


class SYTextStats:
    DESCRIPTION = ("Counts the characters, words and lines of a text and guesses the tokens (characters divided by 4). "
                   "Set a token limit (for example 77) to get a true or false for going over it, and a plain info line.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "INT", "STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("chars", "words", "lines", "est_tokens", "summary", "over_limit", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to count. It passes nothing on, it only measures."}),
            },
            "optional": {
                "token_limit": ("INT", {"default": 0, "min": 0, "max": 10000000, "tooltip": "Your limit in tokens, for example 77 for a prompt. 0 means no limit."}),
            },
        }

    def run(self, text, token_limit=0):
        stats = text_stats(text)
        over, sentence = limit_info(stats[3], token_limit)
        return stats + (summary_text(stats), over, summary_text(stats) + "; " + sentence)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextStats", SYTextStats)
NODE_DISPLAY_NAME_MAPPINGS["SYTextStats"] = "Text Stats SY"
