"""IndexSwitch SY: pick one of up to four inputs by number. Only the chosen branch runs."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


class _Any(str):
    """Matches every ComfyUI type name."""

    def __ne__(self, other):
        return False


ANY = _Any("*")
SLOTS = 4


def pick_index(select, values):
    """Pure function. select is 1-based. values is a list of up to SLOTS items (None = not connected)."""
    if not isinstance(select, int) or select < 1 or select > SLOTS:
        raise ValueError("select must be a whole number from 1 to %d, got %r." % (SLOTS, select))
    value = values[select - 1] if select <= len(values) else None
    if value is None:
        raise ValueError("input%d is not connected. Connect it or change select." % select)
    return value


def wanted_inputs(select, linked):
    """Pure function. Names of the lazy inputs to ask for: the picked one, only when it is connected.

    `linked` is the set of input names that have a link, or None when it is not known (then ask for the picked one).
    Asking for an input with no link makes ComfyUI stop with a hard to read message, so run() gets None and says it clearly.
    """
    if not isinstance(select, int) or select < 1 or select > SLOTS:
        raise ValueError("select must be a whole number from 1 to %d, got %r." % (SLOTS, select))
    name = "input%d" % select
    if linked is not None and name not in linked:
        return []
    return [name]


class SYIndexSwitch:
    DESCRIPTION = "Pick one of up to four inputs by number. Select 1 sends input1, select 2 sends input2, and so on. The inputs you do not pick are not run."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = (ANY, "INT")
    RETURN_NAMES = ("selected_value", "selected_index")

    @classmethod
    def INPUT_TYPES(cls):
        optional = {}
        for i in range(1, SLOTS + 1):
            optional["input%d" % i] = (ANY, {"lazy": True, "tooltip": "Sent when select is %d." % i})
        return {
            "required": {
                "select": ("INT", {"default": 1, "min": 1, "max": SLOTS, "step": 1, "tooltip": "Which input to send, from 1 to %d." % SLOTS}),
            },
            "optional": optional,
            "hidden": {"dynprompt": "DYNPROMPT", "unique_id": "UNIQUE_ID"},
        }

    def check_lazy_status(self, select, input1=None, input2=None, input3=None, input4=None, dynprompt=None, unique_id=None):
        linked = None
        if dynprompt is not None and unique_id is not None:
            try:
                linked = set(dynprompt.get_node(unique_id).get("inputs", {}))
            except Exception:  # unknown shape: fall back to asking for the picked input
                linked = None
        return wanted_inputs(select, linked)

    def run(self, select, input1=None, input2=None, input3=None, input4=None, dynprompt=None, unique_id=None):
        value = pick_index(select, [input1, input2, input3, input4])
        return (value, select)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "IndexSwitch", SYIndexSwitch)
