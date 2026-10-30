"""Seed From Text SY: turns any text into a repeatable seed number."""
import hashlib

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SALT = 2 ** 32 - 1


def seed_from_text(text, salt=0):
    """Pure function. First 8 bytes of SHA-256 of '<salt>:<text>' as a big-endian number, modulo 2**53."""
    if not isinstance(text, str):
        raise ValueError("text must be text, got %r" % (text,))
    if isinstance(salt, bool) or not isinstance(salt, int) or not 0 <= salt <= MAX_SALT:
        raise ValueError("salt must be a whole number from 0 to %d, got %r" % (MAX_SALT, salt))
    digest = hashlib.sha256((str(salt) + ":" + text).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % (2 ** 53)


class SYSeedFromText:
    DESCRIPTION = "Turns any text into a seed number. The same text and salt always give the same seed."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": False, "tooltip": "Any text, such as a name or a prompt. Empty text is allowed."}),
                "salt": ("INT", {"default": 0, "min": 0, "max": MAX_SALT, "step": 1, "tooltip": "Change this number to get a different seed from the same text."}),
            }
        }

    def run(self, text, salt):
        return (seed_from_text(text, salt),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SeedFromText", SYSeedFromText)
NODE_DISPLAY_NAME_MAPPINGS["SYSeedFromText"] = "Seed From Text SY"
