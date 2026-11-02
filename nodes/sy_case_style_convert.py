"""Case Style Convert SY: rewrites a phrase into another naming style (snake_case, camelCase and so on)."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

STYLES = ["snake_case", "kebab-case", "camelCase", "PascalCase", "Title Case", "UPPER_SNAKE"]


def _kind(ch):
    if ch.isdigit():
        return "d"
    if ch.isalpha():
        return "u" if ch.isupper() else "l"
    return None


def split_words(text):
    """Pure function. Splits on spaces, dashes, underscores, symbols, lower-to-upper changes and letter/number changes."""
    words = []
    cur = ""
    for ch in str(text):
        if ch in "'’":
            continue  # apostrophes vanish: don't -> dont
        k = _kind(ch)
        if k is None:
            if cur:
                words.append(cur)
                cur = ""
            continue
        if cur:
            pk = _kind(cur[-1])
            if pk == "l" and k == "u":
                words.append(cur)
                cur = ""
            elif (pk == "d") != (k == "d"):
                words.append(cur)
                cur = ""
            elif pk == "u" and k == "l" and len(cur) >= 2 and _kind(cur[-2]) == "u":
                words.append(cur[:-1])
                cur = cur[-1]
        cur += ch
    if cur:
        words.append(cur)
    return words


def _cap(w):
    return w[:1].upper() + w[1:].lower()


def convert_case(text, style):
    """Pure function. Returns the phrase in the chosen style. Empty text gives empty text."""
    if style not in STYLES:
        raise ValueError("style must be one of: %s (got %r)" % (", ".join(STYLES), style))
    words = split_words(text)
    if not words:
        return ""
    low = [w.lower() for w in words]
    if style == "snake_case":
        return "_".join(low)
    if style == "kebab-case":
        return "-".join(low)
    if style == "UPPER_SNAKE":
        return "_".join(w.upper() for w in words)
    if style == "PascalCase":
        return "".join(_cap(w) for w in words)
    if style == "camelCase":
        return low[0] + "".join(_cap(w) for w in words[1:])
    return " ".join(_cap(w) for w in words)  # Title Case


class SYCaseStyleConvert:
    DESCRIPTION = ("Rewrites a phrase into another naming style, for file names, keys or tags. "
                   "Spaces, dashes, underscores and capital letters mark where the words split.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "tooltip": "The phrase to rewrite. Other symbols are dropped."}),
                "style": (STYLES, {"default": "snake_case", "tooltip": "The naming style you want the phrase in."}),
            },
        }

    def run(self, text, style):
        return (convert_case(text, style),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CaseStyleConvert", SYCaseStyleConvert)
NODE_DISPLAY_NAME_MAPPINGS["SYCaseStyleConvert"] = "Case Style Convert SY"
