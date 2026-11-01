"""Slugify SY: turns any text into a safe, simple name for files, links and ids."""
import re
import unicodedata

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SEPARATORS = ("-", "_")


_RESERVED = {"con", "prn", "aux", "nul"} | {"com%d" % i for i in range(1, 10)} | {"lpt%d" % i for i in range(1, 10)}


def slugify(text, sep, max_length, lowercase, fallback="", windows_safe=False):
    """Pure function. Plain ASCII letters and digits joined by one separator. May return an empty string
    (or the slug of `fallback` when given). windows_safe adds '-file' to names Windows cannot use (con, nul, com1 ...)."""
    return slugify_info(text, sep, max_length, lowercase, fallback, windows_safe)[0]


def slugify_info(text, sep, max_length, lowercase, fallback="", windows_safe=False):
    """Pure function. Returns (slug, info)."""
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
    cut = False
    if max_length and len(slug) > max_length:
        slug = slug[:max_length].strip(sep)
        cut = True
    dropped = len([c for c in text if c.isalnum() and not unicodedata.normalize("NFKD", c).encode("ascii", "ignore")])
    used_fallback = False
    if slug == "" and fallback:
        slug = _plain(str(fallback), sep, max_length, lowercase)
        used_fallback = slug != ""
    if windows_safe and slug.split(".")[0].lower() in _RESERVED:
        slug = slug + sep + "file"
    notes = []
    if text.strip() == "":
        notes.append("the text is empty")
    if dropped:
        notes.append("%d non-Latin character(s) could not be kept" % dropped)
    if cut:
        notes.append("cut to max_length %d" % max_length)
    if used_fallback:
        notes.append("used the fallback because nothing usable was left")
    elif slug == "":
        notes.append("WARNING: the result is empty; set a fallback such as 'untitled' so a file name is never blank")
    info = "Slug %r (%d characters)" % (slug, len(slug))
    if notes:
        info += "; " + "; ".join(notes)
    return slug, info


def _plain(text, sep, max_length, lowercase):
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9]+", sep, plain).strip(sep)
    if lowercase:
        slug = slug.lower()
    if max_length:
        slug = slug[:max_length].strip(sep)
    return slug


class SYSlugify:
    DESCRIPTION = ("Turns any text into a simple name made of letters, digits and one separator. Accents are removed. "
                   "A fallback name stops empty results, windows_safe avoids names like con or nul, and the info line says what was dropped.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("slug", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": False, "tooltip": "The text to turn into a simple name, for example a title."}),
                "separator": (list(SEPARATORS), {"default": "-", "tooltip": "The character placed between words."}),
                "max_length": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1, "tooltip": "Longest result in characters. 0 means no limit."}),
                "lowercase": ("BOOLEAN", {"default": True, "tooltip": "On makes every letter small."}),
            },
            "optional": {
                "fallback": ("STRING", {"default": "", "multiline": False, "tooltip": "Used when nothing is left, for example only Chinese or emoji. Try 'untitled'."}),
                "windows_safe": ("BOOLEAN", {"default": False, "tooltip": "On: names Windows cannot use (con, nul, com1) get '-file' added."}),
            },
        }

    def run(self, text, separator, max_length, lowercase, fallback="", windows_safe=False):
        return slugify_info(text, separator, max_length, lowercase, fallback, windows_safe)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Slugify", SYSlugify)
