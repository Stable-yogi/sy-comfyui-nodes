"""Hash Text SY: turns a text into a short fingerprint code."""
import hashlib

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

ALGORITHMS = ("sha256", "sha1", "md5", "sha512")


FULL_LENGTH = {"sha256": 64, "sha1": 40, "md5": 32, "sha512": 128}


def normalize_text(text):
    """Pure function. Lower case and one space between words, so small typing differences give the same code."""
    return " ".join(text.lower().split())


def hash_info(text, algorithm, length, normalize=False):
    """Pure function. One plain line about the code that was made."""
    full = FULL_LENGTH.get(algorithm, 0)
    kept = length if length and length < full else full
    note = " Fine for file names; not safe for secrets." if algorithm in ("md5", "sha1") else ""
    same = " Capitals and extra spaces were ignored." if normalize else ""
    return "%s of %d characters, code is %d of %d characters.%s%s" % (algorithm, len(text), kept, full, same, note)


def hash_text(text, algorithm, length, strip, normalize=False):
    """Pure function. Returns the lowercase hex digest of the UTF-8 text, cut to `length` (0 = all)."""
    if algorithm not in ALGORITHMS:
        raise ValueError("algorithm must be one of: %s, got %r" % (", ".join(ALGORITHMS), algorithm))
    if not 0 <= length <= 128:
        raise ValueError("length must be between 0 and 128, got %s" % length)
    if strip:
        text = text.strip()
    if normalize:
        text = normalize_text(text)
    digest = hashlib.new(algorithm, text.encode("utf-8")).hexdigest()
    return digest[:length] if length else digest


class SYHashText:
    DESCRIPTION = ("Turns a text into a fingerprint code. The same text always gives the same code. Handy for file names. Can ignore "
                   "capital letters and extra spaces, so two nearly equal prompts get the same code, and an info line says what was made.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("digest", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to fingerprint."}),
                "algorithm": (list(ALGORITHMS), {"default": "sha256", "tooltip": "Which fingerprint method to use. sha256 is a good default."}),
                "length": ("INT", {"default": 0, "min": 0, "max": 128, "tooltip": "Keep only this many characters of the code. 0 keeps all of it."}),
                "strip": ("BOOLEAN", {"default": False, "tooltip": "On: remove spaces and new lines around the text first."}),
            },
            "optional": {
                "normalize": ("BOOLEAN", {"default": False, "tooltip": "On: ignore capital letters and extra spaces, so 'A  Cat' and 'a cat' give the same code."}),
            },
        }

    def run(self, text, algorithm, length, strip, normalize=False):
        return (hash_text(text, algorithm, length, strip, normalize), hash_info(text, algorithm, length, normalize))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "HashText", SYHashText)
NODE_DISPLAY_NAME_MAPPINGS["SYHashText"] = "Hash Text SY"
