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
    "readable": "abcdefghjkmnpqrstuvwxyz23456789",  # no 0 o 1 l i, so a code is easy to read out loud
}
_BAD_NAME_CHARS = set('<>:"/|?*') | {chr(92)}


def make_id(length, charset, seed, prefix="", nonce=None):
    """Pure function. Same inputs give the same id. A nonce (any whole number, such as the clock) makes it a different id."""
    length = int(length)
    if not 4 <= length <= 16:
        raise ValueError("length must be between 4 and 16")
    if charset not in CHARSETS:
        raise ValueError("unknown charset %r - pick one of: %s" % (charset, ", ".join(CHARSETS)))
    rng = random.Random(int(seed) if nonce is None else "%d:%d" % (int(seed), int(nonce)))
    chars = CHARSETS[charset]
    return str(prefix) + "".join(rng.choice(chars) for _ in range(length))


def id_info(code, length, charset, seed, prefix, unique):
    """Pure function. A plain line about the code: how it was made, how many codes are possible, file name warnings."""
    possible = len(CHARSETS[charset]) ** int(length)
    how = "new code every run" if unique else "from seed %d (same seed, same code)" % int(seed)
    text = "%s: %s, %s, %d characters, about %s possible codes" % (code, how, charset, int(length), format(possible, ","))
    if any(c in _BAD_NAME_CHARS for c in str(prefix)):
        text += ". Warning: the prefix has characters that are not allowed in file names"
    return text


class SYShortID:
    DESCRIPTION = ("Makes a short code such as a1b2c3d4. The same seed gives the same code, or switch on new code every run. "
                   "Add a prefix if you like. The readable set avoids look-alike characters (0 o 1 l i). The info line says how many codes are possible.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("short_id", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "length": ("INT", {"default": 8, "min": 4, "max": 16, "tooltip": "How many characters the code has (not counting the prefix)."}),
                "charset": (list(CHARSETS), {"default": "hex", "tooltip": "Which characters may appear: hex, letters, digits, mixed, or readable (no look-alikes)."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "tooltip": "Same seed gives the same code. Change it for a new code."}),
                "prefix": ("STRING", {"default": "", "tooltip": "Text put in front of the code, for example run_."}),
            },
            "optional": {
                "new_each_run": ("BOOLEAN", {"default": False, "tooltip": "On: a different code on every run, whatever the seed. Off: the seed decides."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, new_each_run=False, **kwargs):
        return float("nan") if new_each_run else ""

    def run(self, length, charset, seed, prefix="", new_each_run=False):
        code = make_id(length, charset, seed, prefix, random.SystemRandom().getrandbits(64) if new_each_run else None)
        return (code, id_info(code, length, charset, seed, prefix, bool(new_each_run)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ShortID", SYShortID)
NODE_DISPLAY_NAME_MAPPINGS["SYShortID"] = "Short ID SY"
