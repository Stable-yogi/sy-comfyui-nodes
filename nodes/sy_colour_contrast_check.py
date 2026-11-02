"""Colour Contrast Check SY: tells whether text in one colour is easy to read on another colour."""
try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex, to_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex, to_hex


def _channel(c):
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def brightness(rgb):
    """Pure function. Relative brightness 0..1 of an (r, g, b) colour with floats 0..1."""
    r, g, b = (_channel(min(1.0, max(0.0, float(c)))) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(rgb_a, rgb_b):
    """Pure function. Returns 1.0 (same colour) up to 21.0 (black on white)."""
    la, lb = brightness(rgb_a), brightness(rgb_b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def grade_for(ratio):
    if ratio >= 7.0:
        return "great"
    if ratio >= 4.5:
        return "good"
    if ratio >= 3.0:
        return "ok for large text"
    return "poor"


def check_contrast(foreground, background):
    """Pure function. Hex colour texts in. Returns (ratio, grade, better_text_colour)."""
    fg = parse_hex(foreground, "foreground")
    bg = parse_hex(background, "background")
    black, white = (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)
    better = black if contrast_ratio(black, bg) >= contrast_ratio(white, bg) else white
    ratio = contrast_ratio(fg, bg)
    return ratio, grade_for(ratio), to_hex(better)


class SYColourContrastCheck:
    DESCRIPTION = ("Tells whether text in one colour is easy to read on another colour, for thumbnails and overlays. "
                   "Also names black or white as the better text colour for that background.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "STRING", "STRING")
    RETURN_NAMES = ("ratio", "grade", "better_text_colour")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "foreground": ("STRING", {"default": to_hex((1.0, 1.0, 1.0)), "tooltip": "The text colour as web hex."}),
                "background": ("STRING", {"default": to_hex((0.2, 0.4, 0.8)), "tooltip": "The colour behind the text, as web hex."}),
            },
        }

    def run(self, foreground, background):
        return check_contrast(foreground, background)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ColourContrastCheck", SYColourContrastCheck)
NODE_DISPLAY_NAME_MAPPINGS["SYColourContrastCheck"] = "Colour Contrast Check SY"
