"""Short ID SY: makes a short repeatable code (for names and labels) from a seed."""
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 64 - 1
CHARSETS = {
    "hex": "0123456789abcdef",
    "letters": "abcdefghijklmnopqrstuvwxyz",
    "digits": "0123456789",
    "mixed": "abcdefghijklmnopqrstuvwxyz0123456789",
}


def make_id(length, charset, seed, prefix=""):
    """Pure function. Same inputs give the same id."""
    length = int(length)
    if not 4 <= length <= 16:
        raise ValueError("length must be between 4 and 16")
    if charset not in CHARSETS:
        raise ValueError("unknown charset %r - pick one of: %s" % (charset, ", ".join(CHARSETS)))
    rng = random.Random(int(seed))
    chars = CHARSETS[charset]
    return str(prefix) + "".join(rng.choice(chars) for _ in range(length))


class SYShortID:
    DESCRIPTION = "Makes a short code such as a1b2c3d4. The same seed gives the same code. Add a prefix if you like."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("short_id",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "length": ("INT", {"default": 8, "min": 4, "max": 16, "tooltip": "How many characters the code has (not counting the prefix)."}),
                "charset": (list(CHARSETS), {"default": "hex", "tooltip": "Which characters may appear: hex, letters, digits or mixed."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "tooltip": "Same seed gives the same code. Change it for a new code."}),
                "prefix": ("STRING", {"default": "", "tooltip": "Text put in front of the code, for example run_."}),
            },
        }

    def run(self, length, charset, seed, prefix=""):
        return (make_id(length, charset, seed, prefix),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ShortID", SYShortID)
NODE_DISPLAY_NAME_MAPPINGS["SYShortID"] = "Short ID SY"
