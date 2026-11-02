"""Latch Value SY: remembers the first value it sees and keeps giving it until reset."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

_STORE = {}   # node id -> frozen text. Memory only, nothing is written to disk.


def latch_step(stored, incoming, latch_on=True, reset=False):
    """Pure function. Returns (output, new_stored, is_frozen)."""
    if incoming is not None and not isinstance(incoming, str):
        raise ValueError("value must be text, got %r: convert numbers to text first" % (incoming,))
    if not latch_on:
        return (incoming, None, False)       # pass through and forget
    if reset or stored is None:
        return (incoming, incoming, False)   # take the new value now
    return (stored, stored, True)


class SYLatchValue:
    DESCRIPTION = ("Remembers the first value it sees and keeps giving that same value on later runs until you reset it, "
                   "so a random seed or a made-up name can be frozen on purpose. Memory only, nothing is saved to disk.")
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("value", "is_frozen")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("STRING", {"default": "", "tooltip": "The value to freeze. Numbers go in as text."}),
                "latch_on": ("BOOLEAN", {"default": True, "tooltip": "On: keep the first value. Off: pass values through and forget."}),
                "reset": ("BOOLEAN", {"default": False, "tooltip": "On: forget the stored value and take the new one now."}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")   # check again on every run

    def run(self, value, latch_on=True, reset=False, unique_id=None):
        key = str(unique_id) if unique_id is not None else "default"
        out, new_stored, frozen = latch_step(_STORE.get(key), value, latch_on, reset)
        if new_stored is None:
            _STORE.pop(key, None)
        else:
            _STORE[key] = new_stored
        return (out, frozen)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LatchValue", SYLatchValue)
NODE_DISPLAY_NAME_MAPPINGS["SYLatchValue"] = "Latch Value SY"
