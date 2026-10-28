"""Switch SY: choose between two inputs with one on/off switch. Only the chosen branch runs."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


class _Any(str):
    """Matches every ComfyUI type name."""

    def __ne__(self, other):
        return False


ANY = _Any("*")


def pick(use_a, a, b):
    """Pure function. True gives a, False gives b."""
    return a if use_a else b


class SYSwitch:
    DESCRIPTION = "One switch, two inputs. On sends input A. Off sends input B. The branch you do not pick is not run."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = (ANY,)
    RETURN_NAMES = ("output",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "use_a": ("BOOLEAN", {"default": True, "label_on": "A", "label_off": "B", "tooltip": "On sends input A. Off sends input B."}),
            },
            "optional": {
                "a": (ANY, {"lazy": True, "tooltip": "Sent when the switch is on."}),
                "b": (ANY, {"lazy": True, "tooltip": "Sent when the switch is off."}),
            },
        }

    def check_lazy_status(self, use_a, a=None, b=None):
        return ["a"] if use_a else ["b"]

    def run(self, use_a, a=None, b=None):
        return (pick(use_a, a, b),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Switch", SYSwitch)
