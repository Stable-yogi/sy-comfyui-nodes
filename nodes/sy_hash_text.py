"""Hash Text SY: turns a text into a short fingerprint code."""
import hashlib

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

ALGORITHMS = ("sha256", "sha1", "md5", "sha512")


def hash_text(text, algorithm, length, strip):
    """Pure function. Returns the lowercase hex digest of the UTF-8 text, cut to `length` (0 = all)."""
    if algorithm not in ALGORITHMS:
        raise ValueError("algorithm must be one of: %s, got %r" % (", ".join(ALGORITHMS), algorithm))
    if not 0 <= length <= 128:
        raise ValueError("length must be between 0 and 128, got %s" % length)
    if strip:
        text = text.strip()
    digest = hashlib.new(algorithm, text.encode("utf-8")).hexdigest()
    return digest[:length] if length else digest


class SYHashText:
    DESCRIPTION = "Turns a text into a fingerprint code. The same text always gives the same code. Handy for file names."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("digest",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to fingerprint."}),
                "algorithm": (list(ALGORITHMS), {"default": "sha256", "tooltip": "Which fingerprint method to use. sha256 is a good default."}),
                "length": ("INT", {"default": 0, "min": 0, "max": 128, "tooltip": "Keep only this many characters of the code. 0 keeps all of it."}),
                "strip": ("BOOLEAN", {"default": False, "tooltip": "On: remove spaces and new lines around the text first."}),
            }
        }

    def run(self, text, algorithm, length, strip):
        return (hash_text(text, algorithm, length, strip),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "HashText", SYHashText)
NODE_DISPLAY_NAME_MAPPINGS["SYHashText"] = "Hash Text SY"
