"""Slugify SY: turns any text into a safe, simple name for files, links and ids."""
import re
import unicodedata

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SEPARATORS = ("-", "_")


def slugify(text, sep, max_length, lowercase):
    """Pure function. Plain ASCII letters and digits joined by one separator. May return an empty string."""
    if not isinstance(text, str):
        raise ValueError("text must be text, got %r" % (text,))
    if sep not in SEPARATORS:
        raise ValueError("separator must be one of: %s, got %r" % (", ".join(SEPARATORS), sep))
    if max_length < 0 or max_length > 255:
        raise ValueError("max_length must be between 0 and 255 (0 means no limit), got %s" % max_length)
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9]+", sep, plain).strip(sep)
    if lowercase:
        slug = slug.lower()
    if max_length:
        slug = slug[:max_length].strip(sep)
    return slug


class SYSlugify:
    DESCRIPTION = "Turns any text into a simple name made of letters, digits and one separator. Accents are removed."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("slug",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": False, "tooltip": "The text to turn into a simple name, for example a title."}),
                "separator": (list(SEPARATORS), {"default": "-", "tooltip": "The character placed between words."}),
                "max_length": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "tooltip": "Longest result in characters. 0 means no limit."}),
                "lowercase": ("BOOLEAN", {"default": True, "tooltip": "On makes every letter small."}),
            }
        }

    def run(self, text, separator, max_length, lowercase):
        return (slugify(text, separator, max_length, lowercase),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Slugify", SYSlugify)
