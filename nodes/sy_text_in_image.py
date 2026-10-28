"""Text In Image SY: writes a phrase that asks an image model to draw exact text at a chosen place."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

PLACEMENTS = ("top", "centre", "bottom", "left", "right", "on_sign", "on_shirt", "on_poster")
_WHERE = {
    "top": "at the top of the picture",
    "centre": "in the centre of the picture",
    "bottom": "at the bottom of the picture",
    "left": "on the left side of the picture",
    "right": "on the right side of the picture",
    "on_sign": "on a sign in the scene",
    "on_shirt": "on the shirt",
    "on_poster": "on a poster in the scene",
}


def build_text_phrase(text, placement, style_words="", language_hint=""):
    """Pure function. Returns the phrase."""
    t = str(text or "").strip()
    if not t:
        raise ValueError("text is empty: type the words that should appear in the picture")
    if '"' in t or "“" in t or "”" in t:
        raise ValueError("text contains double quote marks: remove them, the node adds its own")
    if placement not in _WHERE:
        raise ValueError("unknown placement %r: choose one of %s" % (placement, ", ".join(PLACEMENTS)))
    phrase = 'Write the exact text "%s" %s' % (t, _WHERE[placement])
    s = " ".join(str(style_words or "").split()).strip(" ,.")
    if s:
        phrase += ", in " + s
    phrase += "."
    lang = " ".join(str(language_hint or "").split()).strip(" ,.")
    if lang:
        phrase += " The text is in %s." % lang
    return phrase


class SYTextInImage:
    DESCRIPTION = "Writes a phrase that asks for exact words to appear in the picture at a place you choose. The words are put in double quotes."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("phrase",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "tooltip": "The exact words to show. Do not type double quote marks."}),
                "placement": (list(PLACEMENTS), {"default": "top", "tooltip": "Where the words should appear."}),
            },
            "optional": {
                "style_words": ("STRING", {"default": "", "tooltip": "How the letters look, for example 'bold white capital letters'."}),
                "language_hint": ("STRING", {"default": "", "tooltip": "Optional language name, for example 'German'."}),
            },
        }

    def run(self, text, placement, style_words="", language_hint=""):
        return (build_text_phrase(text, placement, style_words, language_hint),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextInImage", SYTextInImage)
