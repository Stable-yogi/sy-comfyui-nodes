"""Text Truncate SY: shortens a text to a maximum length and adds a short ending."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_TRAIL = " \t\r\n,;:"


CUT_FROM = ("end (keep the start)", "middle (keep both ends)")


def truncate_text(text, max_chars, suffix, at_word, cut_from=CUT_FROM[0]):
    """Pure function. Returns (text, truncated). The result with the suffix is at most max_chars long.
    cut_from middle keeps the start and the end and puts the suffix between (good for long file names)."""
    if cut_from not in CUT_FROM:
        raise ValueError("cut_from must be one of: %s" % ", ".join(CUT_FROM))
    if not 1 <= max_chars <= 100000:
        raise ValueError("max_chars must be between 1 and 100000, got %s" % max_chars)
    if len(text) <= max_chars:
        return (text, False)
    if len(suffix) > max_chars:
        raise ValueError("suffix is longer than max_chars; shorten the suffix or raise max_chars")
    limit = max_chars - len(suffix)
    if cut_from == CUT_FROM[1]:
        tail = limit // 2
        head = limit - tail
        return (text[:head].rstrip() + suffix + (text[len(text) - tail:].lstrip() if tail else ""), True)
    cut = text[:limit]
    if at_word and not text[limit].isspace():
        idx = max(cut.rfind(" "), cut.rfind("\n"), cut.rfind("\t"))
        if idx > 0:
            cut = cut[:idx]
    cut = cut.rstrip(_TRAIL)
    return (cut + suffix, True)


def truncate_info(original, result, truncated, max_chars):
    """Pure function. One plain line: was the text cut and by how much."""
    if not truncated:
        return "Fits: %d of %d characters, nothing cut" % (len(original), max_chars)
    return "Shortened %d -> %d characters (%d removed, limit %d)" % (len(original), len(result), len(original) - len(result), max_chars)


class SYTextTruncate:
    DESCRIPTION = ("Shortens a text to a maximum length and adds an ending such as three dots. Can cut at a word end, or keep both ends and cut the middle "
                   "(good for long file names). The info line says how much was removed.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("text", "truncated", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to shorten."}),
                "max_chars": ("INT", {"default": 100, "min": 1, "max": 100000, "tooltip": "Longest allowed result, counting the ending."}),
                "suffix": ("STRING", {"default": "...", "tooltip": "Added at the end when the text was cut. Leave empty for none."}),
                "at_word": ("BOOLEAN", {"default": True, "tooltip": "On: cut back to the end of a whole word. Off: cut at the exact character."}),
            },
            "optional": {
                "cut_from": (list(CUT_FROM), {"default": CUT_FROM[0], "tooltip": "End keeps the start. Middle keeps both ends and puts the ending in the middle. at_word is ignored for middle."}),
            },
        }

    def run(self, text, max_chars, suffix, at_word, cut_from=CUT_FROM[0]):
        out, truncated = truncate_text(text, max_chars, suffix, at_word, cut_from)
        return (out, truncated, truncate_info(text, out, truncated, max_chars))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextTruncate", SYTextTruncate)
NODE_DISPLAY_NAME_MAPPINGS["SYTextTruncate"] = "Text Truncate SY"
