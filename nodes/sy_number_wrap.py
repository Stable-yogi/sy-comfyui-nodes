"""Number Wrap SY: keeps a number inside a range by wrapping, bouncing or clamping."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("wrap", "ping_pong", "clamp")


def wrap_number(value, low, high, mode):
    """Pure function. Returns (result, info)."""
    value = float(value)
    low = float(low)
    high = float(high)
    if not high > low:
        raise ValueError("high must be bigger than low, got low=%s high=%s" % (low, high))
    if mode not in MODES:
        raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))
    span = high - low
    if mode == "wrap":
        result = low + (value - low) % span
    elif mode == "ping_pong":
        t = (value - low) % (2.0 * span)
        if t > span:
            t = 2.0 * span - t
        result = low + t
    else:
        result = min(max(value, low), high)
    return result, "%s: %s -> %s (range %s to %s)" % (mode, value, result, low, high)


class SYNumberWrap:
    DESCRIPTION = "Keeps a number inside a range. It can wrap round, bounce back and forth, or stop at the edges."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "STRING")
    RETURN_NAMES = ("result", "info")

    @classmethod
    def INPUT_TYPES(cls):
        big = 1.0e9
        return {
            "required": {
                "value": ("FLOAT", {"default": 0.0, "min": -big, "max": big, "step": 0.01, "tooltip": "The number to keep inside the range."}),
                "low": ("FLOAT", {"default": 0.0, "min": -big, "max": big, "step": 0.01, "tooltip": "Lowest allowed number."}),
                "high": ("FLOAT", {"default": 1.0, "min": -big, "max": big, "step": 0.01, "tooltip": "Highest allowed number. Must be bigger than low."}),
                "mode": (list(MODES), {"default": "wrap", "tooltip": "wrap loops round, ping_pong bounces back, clamp stops at the edge."}),
            }
        }

    def run(self, value, low, high, mode):
        return wrap_number(value, low, high, mode)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "NumberWrap", SYNumberWrap)
