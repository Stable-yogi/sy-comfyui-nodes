"""Clamp Remap SY: keeps a number inside a range and maps it from one range to another."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def _num(name, v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ValueError("%s must be a normal number, got %r." % (name, v))
    return float(v)


def clamp_remap(value, in_min, in_max, out_min, out_max, clamp=True):
    """Pure function. Returns (remapped, clamped).
    clamped = value held inside the input range. remapped = value moved linearly from the input range to the output range."""
    value = _num("value", value)
    in_min, in_max = _num("in_min", in_min), _num("in_max", in_max)
    out_min, out_max = _num("out_min", out_min), _num("out_max", out_max)
    if in_min == in_max:
        raise ValueError("in_min and in_max are both %g. Make them different so the range has a size." % in_min)
    lo, hi = min(in_min, in_max), max(in_min, in_max)
    clamped = min(max(value, lo), hi)
    src = clamped if clamp else value
    t = (src - in_min) / (in_max - in_min)
    return out_min + t * (out_max - out_min), clamped


def remap_info(value, in_min, in_max, out_min, out_max, clamp=True):
    """Pure function. Returns (was_outside, info). was_outside is true when value sits outside the input range."""
    result, clamped = clamp_remap(value, in_min, in_max, out_min, out_max, clamp)
    lo, hi = min(in_min, in_max), max(in_min, in_max)
    outside = value < lo or value > hi
    text = "%g in %g..%g -> %g in %g..%g" % (value, in_min, in_max, result, out_min, out_max)
    if outside and clamp:
        text += " (value was outside the input range, held at %g)" % clamped
    elif outside:
        text += " (value is outside the input range, clamp is off so the result runs past the output range)"
    return outside, text


class SYClampRemap:
    DESCRIPTION = "Keeps a number inside a range, and moves it from one range to another. Example: 0 to 1 becomes 0 to 255. Also tells you when the number was outside the range, with a plain info line."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "FLOAT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("remapped", "clamped", "was_outside", "info")

    @classmethod
    def INPUT_TYPES(cls):
        def num(default, tip):
            return ("FLOAT", {"default": default, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": tip})
        return {
            "required": {
                "value": num(0.5, "The number to change."),
                "in_min": num(0.0, "Start of the range the number comes from."),
                "in_max": num(1.0, "End of the range the number comes from. Must differ from in_min."),
                "out_min": num(0.0, "Start of the range the number goes to."),
                "out_max": num(100.0, "End of the range the number goes to."),
                "clamp": ("BOOLEAN", {"default": True, "tooltip": "On keeps the result inside the output range. Off lets it run past."}),
            }
        }

    def run(self, value, in_min, in_max, out_min, out_max, clamp):
        outside, info = remap_info(value, in_min, in_max, out_min, out_max, clamp)
        return clamp_remap(value, in_min, in_max, out_min, out_max, clamp) + (outside, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ClampRemap", SYClampRemap)
NODE_DISPLAY_NAME_MAPPINGS["SYClampRemap"] = "Clamp Remap SY"
