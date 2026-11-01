"""Repeater SY: one value in, the same value out on eight outputs."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


class _Any(str):
    """Matches every ComfyUI type name."""

    def __ne__(self, other):
        return False


ANY = _Any("*")
OUTPUTS = 8


def fan_out(value, count=OUTPUTS):
    """Pure function. Returns `count` references to the very same object (no copy)."""
    if isinstance(count, bool) or not isinstance(count, int) or count < 1 or count > 16:
        raise ValueError("count must be a whole number from 1 to 16, got %r" % (count,))
    return tuple(value for _ in range(count))


class SYRepeater:
    DESCRIPTION = "Takes one value and sends the same value out on eight outputs, so one wire does not have to be split by hand."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = (ANY,) * OUTPUTS
    RETURN_NAMES = tuple("out_%d" % i for i in range(1, OUTPUTS + 1))

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": (ANY, {"tooltip": "Any value. It is sent out unchanged on all eight outputs."}),
            },
        }

    def run(self, value):
        return fan_out(value, OUTPUTS)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Repeater", SYRepeater)
