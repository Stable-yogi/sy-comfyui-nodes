"""Colour Swatch SY: turns a colour code like d4a537 into numbers, clean text and a small swatch picture."""

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SWATCH_SIZE = 64


def parse_colour(text):
    """Pure function. Accepts 'd4a537', 'd4a' or either with a leading hash sign. Returns (r, g, b)."""
    raw = str(text).strip()
    if raw.startswith("#"):
        raw = raw[1:]
    if len(raw) == 3:
        raw = "".join(ch * 2 for ch in raw)
    if len(raw) != 6 or any(ch not in "0123456789abcdefABCDEF" for ch in raw):
        raise ValueError("colour %r is not valid - use 3 or 6 hex digits such as d4a537, with or without a leading #" % (str(text),))
    return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)


def normalise_colour(rgb):
    """Pure function. (212, 165, 55) -> 'd4a537' with a leading hash sign."""
    return "#%02x%02x%02x" % tuple(rgb)


def colour_info(rgb):
    """Pure function. Returns a plain line: the code, the numbers, and whether black or white text reads best on it."""
    r, g, b = rgb
    lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
    return "%s = rgb(%d, %d, %d), %s colour, %s text reads best" % (
        normalise_colour(rgb), r, g, b, "light" if lum >= 0.5 else "dark", "black" if lum >= 0.5 else "white")


class SYColourSwatch:
    DESCRIPTION = "Reads a colour code (like d4a537), gives red, green and blue numbers, a clean code, a small colour picture and an info line that says if black or white text reads best on it."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("r", "g", "b", "hex", "swatch", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "colour": ("STRING", {"default": "d4a537", "tooltip": "A hex colour: 3 or 6 digits, with or without the # sign."}),
            },
        }

    def run(self, colour):
        import torch  # lazy: the selftest Python has no torch

        rgb = parse_colour(colour)
        values = torch.tensor([c / 255.0 for c in rgb], dtype=torch.float32)
        swatch = values.view(1, 1, 1, 3).expand(1, SWATCH_SIZE, SWATCH_SIZE, 3).contiguous()
        return (rgb[0], rgb[1], rgb[2], normalise_colour(rgb), swatch, colour_info(rgb))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ColourSwatch", SYColourSwatch)
NODE_DISPLAY_NAME_MAPPINGS["SYColourSwatch"] = "Colour Swatch SY"
