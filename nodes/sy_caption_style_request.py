"""Caption Style Request SY: builds the text of a request that asks an LLM to caption an image in a chosen style."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

STYLES = {
    "short": "Write one short sentence of at most {words} words that names the main subject and what it is doing.",
    "detailed": "Write a detailed description of at most {words} words: subject, clothing or materials, setting, colours, light and camera angle.",
    "tags": "Write a comma separated list of short lowercase tags, at most {words} words in total. Cover subject, setting, colours, light and style.",
    "training caption": "Write one plain caption for model training, at most {words} words. Use natural sentences. Describe only what is visible. Do not start with 'a picture of' or 'this image shows'.",
}
STYLE_NAMES = tuple(STYLES)
DEFAULT_WORDS = {"short": 20, "detailed": 120, "tags": 40, "training caption": 60}


def caption_request(style="short", max_words=0, trigger_word="", subject_hint="", notes=""):
    """Pure function. max_words 0 means use the default for the style. It only builds text, it never calls an LLM."""
    if style not in STYLES:
        raise ValueError("style must be one of: %s (got %r)" % (", ".join(STYLE_NAMES), style))
    max_words = int(max_words)
    if max_words < 0:
        raise ValueError("max_words must be 0 (automatic) or more, got %d" % max_words)
    for label, value in (("trigger_word", trigger_word), ("subject_hint", subject_hint), ("notes", notes)):
        if not isinstance(value, str):
            raise ValueError("%s must be text, got %s" % (label, type(value).__name__))
    words = max_words or DEFAULT_WORDS[style]
    lines = ["Look at the attached image and write a caption.", STYLES[style].format(words=words)]
    if subject_hint.strip():
        lines.append("The main subject is: " + subject_hint.strip() + ".")
    if trigger_word.strip():
        lines.append("Begin the caption with the exact word or phrase: " + trigger_word.strip())
    if notes.strip():
        lines.append("Also: " + notes.strip())
    lines.append("Do not guess names or ages. Reply with the caption only.")
    return "\n".join(lines)


class SYCaptionStyleRequest:
    DESCRIPTION = "Builds a request that asks an LLM to caption an image: short, detailed, tags or training caption. It only builds the text."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("request",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "style": (list(STYLE_NAMES), {"default": "short", "tooltip": "What kind of caption you want back."}),
                "max_words": ("INT", {"default": 0, "min": 0, "max": 2000, "tooltip": "Word limit for the caption. 0 uses a sensible limit for the style."}),
            },
            "optional": {
                "trigger_word": ("STRING", {"default": "", "tooltip": "A word the caption must start with, often used in training."}),
                "subject_hint": ("STRING", {"default": "", "tooltip": "What the image shows, if you know it. Helps the model."}),
                "notes": ("STRING", {"multiline": True, "default": "", "tooltip": "Extra wishes, for example: mention the background."}),
            },
        }

    def run(self, style, max_words, trigger_word="", subject_hint="", notes=""):
        return (caption_request(style, max_words, trigger_word, subject_hint, notes),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CaptionStyleRequest", SYCaptionStyleRequest)
NODE_DISPLAY_NAME_MAPPINGS["SYCaptionStyleRequest"] = "Caption Style Request SY"
