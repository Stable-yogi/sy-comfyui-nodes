"""Pixel Count Info SY: megapixels and a short text report for a width and height."""
import math

try:
    from ._sy_common import category, register
    from ._sy_a1_sizes import SNAP_CHOICES, SNAP_DIRECTIONS, snap_choice, snap_value, scale_to_megapixels
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_a1_sizes import SNAP_CHOICES, SNAP_DIRECTIONS, snap_choice, snap_value, scale_to_megapixels

MAX_SIDE = 1_000_000


def pixel_info(width, height):
    """Pure function. Returns (megapixels, pixels, report_text)."""
    width, height = int(width), int(height)
    if width < 0 or height < 0:
        raise ValueError("width and height cannot be negative, got %dx%d" % (width, height))
    pixels = width * height
    mp = pixels / 1_000_000
    if width == 0 or height == 0:
        shape = "no shape (a side is 0)"
        orient = "empty"
    else:
        g = math.gcd(width, height)
        shape = "%d:%d (%.3f)" % (width // g, height // g, width / height)
        orient = "square" if width == height else ("landscape" if width > height else "portrait")
    text = "%dx%d, %d pixels, %.3f megapixels, aspect %s, %s" % (width, height, pixels, mp, shape, orient)
    return (mp, pixels, text)


BIG_MEGAPIXELS = 4.0


def fit_size(width, height, snap_to="off", snap_direction="nearest", target_mp=0.0):
    """Pure function. Returns (out_width, out_height, note).

    target_mp above 0 first scales the size to about that many megapixels (same shape). snap_to then rounds both
    sides to a multiple (8, 16, 32 or 64). With target_mp 0 and snap_to off the size comes back unchanged.
    """
    width, height = int(width), int(height)
    if width < 0 or height < 0:
        raise ValueError("width and height cannot be negative, got %dx%d" % (width, height))
    multiple = snap_choice(snap_to)
    target = float(target_mp)
    if not (0.0 <= target <= 1000.0):  # also rejects nan
        raise ValueError("target_mp must be between 0 and 1000, got %s" % target_mp)
    notes = []
    w, h = float(width), float(height)
    if target > 0:
        if width == 0 or height == 0:
            raise ValueError("cannot scale to %g MP: a side is 0 (%dx%d). Give width and height above 0." % (target, width, height))
        w, h = scale_to_megapixels(width, height, target)
        notes.append("scaled to about %g MP" % target)
    if multiple:
        if width == 0 or height == 0:
            raise ValueError("cannot snap a size with a side of 0 (%dx%d). Give width and height above 0." % (width, height))
        w = snap_value(w, multiple, snap_direction, minimum=multiple)
        h = snap_value(h, multiple, snap_direction, minimum=multiple)
        notes.append("snapped to a multiple of %d (%s)" % (multiple, snap_direction))
    out_w, out_h = int(round(w)), int(round(h))
    mp = out_w * out_h / 1_000_000
    text = ("%dx%d" % (out_w, out_h)) + ((" (" + ", ".join(notes) + ")") if notes else "")
    flags = []
    if out_w and out_h:
        for step in (64, 16, 8):
            if out_w % step == 0 and out_h % step == 0:
                flags.append("multiple of %d" % step)
                break
        else:
            flags.append("not a multiple of 8")
    if mp > BIG_MEGAPIXELS:
        flags.append("large: many cards run out of memory above %d MP" % int(BIG_MEGAPIXELS))
    if flags:
        text += "; " + ", ".join(flags)
    return out_w, out_h, text


class SYPixelCountInfo:
    DESCRIPTION = ("Shows how big a picture size is: megapixels, total pixels and shape. Also gives a text line you can show or save. "
                   "Adds an optional fit: scale to a target number of megapixels and/or snap to a multiple of 8, 16, 32 or 64, "
                   "with the new width and height as outputs and a plain note about size problems.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "INT", "STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("megapixels", "pixels", "report", "out_width", "out_height", "fit_note")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 0, "max": MAX_SIDE, "tooltip": "Width in pixels."}),
                "height": ("INT", {"default": 1024, "min": 0, "max": MAX_SIDE, "tooltip": "Height in pixels."}),
            },
            "optional": {
                "snap_to": (SNAP_CHOICES, {"default": "off", "tooltip": "Round the size to a multiple of this (8, 16, 32, 64). off leaves it alone."}),
                "snap_direction": (SNAP_DIRECTIONS, {"default": "nearest", "tooltip": "How snap_to rounds: nearest multiple, always down, or always up."}),
                "target_mp": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1000.0, "step": 0.05, "tooltip": "0 = off. 1.0 scales the size to about 1 megapixel, same shape."}),
            },
        }

    def run(self, width, height, snap_to="off", snap_direction="nearest", target_mp=0.0):
        out_w, out_h, note = fit_size(width, height, snap_to, snap_direction, target_mp)
        return pixel_info(width, height) + (out_w, out_h, note)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PixelCountInfo", SYPixelCountInfo)
NODE_DISPLAY_NAME_MAPPINGS["SYPixelCountInfo"] = "Pixel Count Info SY"
