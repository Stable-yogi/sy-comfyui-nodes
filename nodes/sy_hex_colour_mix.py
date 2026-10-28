"""Hex Colour Mix SY: blends two colours written as hex text."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_HASH = chr(35)
_DIGITS = "0123456789abcdefABCDEF"


def parse_colour(text):
    """Pure function. Accepts 3 or 6 hex digits, with or without the leading hash. Returns (r, g, b)."""
    s = str(text).strip()
    if s.startswith(_HASH):
        s = s[1:]
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6 or any(ch not in _DIGITS for ch in s):
        raise ValueError("colour must be 3 or 6 hex digits like the ones in a web colour, got %r" % (text,))
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def mix_colours(colour_a, colour_b, amount):
    """Pure function. amount 0 gives colour_a, 1 gives colour_b. Returns (hex_text, r, g, b)."""
    amount = float(amount)
    if amount < 0.0 or amount > 1.0:
        raise ValueError("amount must be between 0 and 1, got %s" % amount)
    a = parse_colour(colour_a)
    b = parse_colour(colour_b)
    r, g, bl = [int(round(x + (y - x) * amount)) for x, y in zip(a, b)]
    return _HASH + "%02x%02x%02x" % (r, g, bl), r, g, bl


class SYHexColourMix:
    DESCRIPTION = "Blends two colours given as hex text. Amount 0 keeps the first colour and 1 gives the second."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT", "INT")
    RETURN_NAMES = ("hex", "r", "g", "b")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "colour_a": ("STRING", {"default": "000000", "multiline": False, "tooltip": "First colour as 3 or 6 hex digits. The # sign is optional."}),
                "colour_b": ("STRING", {"default": "ffffff", "multiline": False, "tooltip": "Second colour as 3 or 6 hex digits. The # sign is optional."}),
                "amount": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "0 gives the first colour, 1 gives the second, 0.5 the middle."}),
            }
        }

    def run(self, colour_a, colour_b, amount):
        return mix_colours(colour_a, colour_b, amount)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "HexColourMix", SYHexColourMix)
