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


def summary_text(stats):
    chars, words, lines, tokens = stats
    return "%d chars, %d words, %d lines, about %d tokens" % (chars, words, lines, tokens)


class SYTextStats:
    DESCRIPTION = "Counts the characters, words and lines of a text and guesses the tokens (characters divided by 4)."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "INT", "STRING")
    RETURN_NAMES = ("chars", "words", "lines", "est_tokens", "summary")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The text to count. It passes nothing on, it only measures."}),
            },
        }

    def run(self, text):
        stats = text_stats(text)
        return stats + (summary_text(stats),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextStats", SYTextStats)
NODE_DISPLAY_NAME_MAPPINGS["SYTextStats"] = "Text Stats SY"
