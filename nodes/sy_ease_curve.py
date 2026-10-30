"""Ease Curve SY: maps a 0 to 1 position through a smooth curve and scales it between two numbers."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

CURVES = ("linear", "ease_in_quad", "ease_out_quad", "ease_in_out_quad", "ease_in_cubic", "ease_out_cubic",
          "ease_in_out_cubic", "smoothstep", "smootherstep")


def ease(t, curve):
    """Pure function. t in 0..1 -> eased value in 0..1."""
    if curve not in CURVES:
        raise ValueError("curve must be one of: %s, got %r" % (", ".join(CURVES), curve))
    if not 0.0 <= t <= 1.0:
        raise ValueError("t must be between 0 and 1, got %s" % t)
    if curve == "linear":
        return t
    if curve == "ease_in_quad":
        return t * t
    if curve == "ease_out_quad":
        return 1.0 - (1.0 - t) ** 2
    if curve == "ease_in_out_quad":
        return 2.0 * t * t if t < 0.5 else 1.0 - (-2.0 * t + 2.0) ** 2 / 2.0
    if curve == "ease_in_cubic":
        return t ** 3
    if curve == "ease_out_cubic":
        return 1.0 - (1.0 - t) ** 3
    if curve == "ease_in_out_cubic":
        return 4.0 * t ** 3 if t < 0.5 else 1.0 - (-2.0 * t + 2.0) ** 3 / 2.0
    if curve == "smoothstep":
        return 3.0 * t ** 2 - 2.0 * t ** 3
    return 6.0 * t ** 5 - 15.0 * t ** 4 + 10.0 * t ** 3


def ease_value(t, curve, start, end):
    """Pure function. Returns (value, eased)."""
    e = ease(t, curve)
    return (start + (end - start) * e, e)


class SYEaseCurve:
    DESCRIPTION = "Turns a position from 0 to 1 into a smooth curve value, then scales it between a start and an end number."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "FLOAT")
    RETURN_NAMES = ("value", "eased")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "t": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "How far along, from 0 (start) to 1 (end)."}),
                "curve": (list(CURVES), {"default": "smoothstep", "tooltip": "The shape of the movement. in starts slow, out ends slow, in_out does both."}),
                "start": ("FLOAT", {"default": 0.0, "min": -1e9, "max": 1e9, "step": 0.01, "tooltip": "The result when t is 0."}),
                "end": ("FLOAT", {"default": 1.0, "min": -1e9, "max": 1e9, "step": 0.01, "tooltip": "The result when t is 1."}),
            }
        }

    def run(self, t, curve, start, end):
        return ease_value(t, curve, start, end)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EaseCurve", SYEaseCurve)
NODE_DISPLAY_NAME_MAPPINGS["SYEaseCurve"] = "Ease Curve SY"
