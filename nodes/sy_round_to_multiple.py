"""Round To Multiple SY: rounds a number to the nearest, next higher or next lower multiple of a step."""
import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("nearest", "up", "down")


def round_to_multiple(value, multiple, mode="nearest"):
    """Pure function. Returns (float, int). Example: 70 with multiple 64 and mode nearest gives 64."""
    for name, v in (("value", value), ("multiple", multiple)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError("%s must be a normal number, got %r." % (name, v))
    if multiple <= 0:
        raise ValueError("multiple must be bigger than 0, got %r. Use a step like 8 or 64." % (multiple,))
    if mode not in MODES:
        raise ValueError("mode must be one of %s, got %r." % (", ".join(MODES), mode))
    q = value / multiple
    # a tiny nudge stops 0.3/0.1 style float noise from tipping the result
    qr = round(q)
    if abs(q - qr) < 1e-9:
        n = qr
    elif mode == "up":
        n = math.ceil(q)
    elif mode == "down":
        n = math.floor(q)
    else:
        n = math.floor(abs(q) + 0.5) * (1 if q >= 0 else -1)
    result = n * multiple
    if isinstance(multiple, float) or isinstance(value, float):
        result = round(result, 10)
    return float(result), int(math.floor(abs(result) + 0.5)) * (1 if result >= 0 else -1)


class SYRoundToMultiple:
    DESCRIPTION = "Rounds a number to a multiple of a step, like 64 for image sizes. Choose nearest, round up or round down."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("float", "int")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {"default": 100.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": "The number to round."}),
                "multiple": ("FLOAT", {"default": 64.0, "min": 0.000001, "max": 1e15, "step": 0.01, "tooltip": "Round to a whole number of these steps. Must be above 0."}),
                "mode": (list(MODES), {"default": "nearest", "tooltip": "nearest goes to the closest step. up goes higher. down goes lower."}),
            }
        }

    def run(self, value, multiple, mode):
        return round_to_multiple(value, multiple, mode)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RoundToMultiple", SYRoundToMultiple)
NODE_DISPLAY_NAME_MAPPINGS["SYRoundToMultiple"] = "Round To Multiple SY"
