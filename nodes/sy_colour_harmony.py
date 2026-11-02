"""Colour Harmony SY: from one colour, makes a matching set of colours."""
import colorsys

try:
    from ._sy_common import category, register
    from ._sy_hexcolour import parse_hex, to_hex
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_hexcolour import parse_hex, to_hex

SCHEMES = ["complementary", "triad", "tetrad", "analogous", "split complementary"]


def harmony_hues(hue_degrees, scheme="triad", spread=30.0):
    """Pure function. Returns hue angles (0..360), the input hue first."""
    if scheme not in SCHEMES:
        raise ValueError("scheme must be one of: %s (got %r)" % (", ".join(SCHEMES), scheme))
    if isinstance(spread, bool) or not isinstance(spread, (int, float)) or not 10 <= spread <= 60:
        raise ValueError("spread must be a number from 10 to 60 degrees, got %r" % (spread,))
    h = float(hue_degrees)
    if scheme == "complementary":
        offsets = [0, 180]
    elif scheme == "triad":
        offsets = [0, 120, 240]
    elif scheme == "tetrad":
        offsets = [0, 90, 180, 270]
    elif scheme == "analogous":
        offsets = [0, -spread, spread]
    else:
        offsets = [0, 180 - spread, 180 + spread]
    return [(h + o) % 360.0 for o in offsets]


def harmony_palette(colour, scheme="triad", spread=30.0):
    """Pure function. Hex colour text in, list of hex colour texts out (input colour first, same saturation and brightness)."""
    rgb = parse_hex(colour, "colour")
    hue, sat, val = colorsys.rgb_to_hsv(*rgb)
    out = [to_hex(rgb)]
    for deg in harmony_hues(hue * 360.0, scheme, spread)[1:]:
        out.append(to_hex(colorsys.hsv_to_rgb(deg / 360.0, sat, val)))
    return out


class SYColourHarmony:
    DESCRIPTION = ("From one colour, makes a matching set of colours (opposite, three-way, four-way, neighbours) "
                   "for a palette or overlay. Saturation and brightness stay the same.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("palette", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "colour": ("STRING", {"default": to_hex((0.2, 0.4, 0.8)), "tooltip": "The starting colour as web hex, such as the default one."}),
                "scheme": (SCHEMES, {"default": "triad", "tooltip": "Which colours go with it: opposite, three-way, four-way, neighbours or split."}),
                "spread": ("FLOAT", {"default": 30.0, "min": 10.0, "max": 60.0, "step": 1.0, "tooltip": "Degrees apart for analogous and split complementary."}),
            },
        }

    def run(self, colour, scheme="triad", spread=30.0):
        pal = harmony_palette(colour, scheme, float(spread))
        return (",".join(pal), len(pal))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ColourHarmony", SYColourHarmony)
NODE_DISPLAY_NAME_MAPPINGS["SYColourHarmony"] = "Colour Harmony SY"
