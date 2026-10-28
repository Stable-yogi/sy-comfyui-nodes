"""Run Timer SY: passes any value through and reports seconds since the first call of this node."""
import time

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


class AnyType(str):
    """ComfyUI any-type trick: never reports a type mismatch."""

    def __ne__(self, other):
        return False


ANY = AnyType("*")
_starts = {}  # unique_id -> time of the first call


def format_elapsed(seconds):
    """Pure function. 65.3 -> '1m 05.3s', 5.0 -> '5.0s' (one decimal)."""
    seconds = max(0.0, float(seconds))
    tenths = int(seconds * 10 + 0.5)
    mins, rest = divmod(tenths, 600)
    if mins:
        return "%dm %04.1fs" % (mins, rest / 10.0)
    return "%.1fs" % (rest / 10.0)


def elapsed_for(key, reset=False, now=None):
    """Seconds since the first call for key; reset=True restarts the clock. now is for tests."""
    now = time.monotonic() if now is None else now
    if reset or key not in _starts:
        _starts[key] = now
    return now - _starts[key]


class SYRunTimer:
    DESCRIPTION = "Passes any value through and tells how many seconds passed since this node first ran. Turn on reset to restart the clock."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = (ANY, "FLOAT")
    RETURN_NAMES = ("value", "elapsed_seconds")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": (ANY, {"tooltip": "Anything you pass through. It comes out unchanged, and the timer measures the time."}),
                "reset": ("BOOLEAN", {"default": False, "tooltip": "On: restart the timer from zero on this run."}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return float("nan")

    def run(self, value, reset=False, unique_id=None):
        return (value, elapsed_for(unique_id, bool(reset)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RunTimer", SYRunTimer)
NODE_DISPLAY_NAME_MAPPINGS["SYRunTimer"] = "Run Timer SY"
