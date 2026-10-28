"""Counter SY: a number that goes up by a step on each run. It keeps no memory: you give it the run number."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

LIMIT = 2 ** 53 - 1


def counter_value(run_index, start, step, max_value, wrap=True):
    """Pure function. value = start + step * run_index.
    With wrap on, the value stays between start and max_value (both included) and starts over past the end.
    With a negative step it counts down from start and wraps back up to max_value."""
    for name, v in (("run_index", run_index), ("start", start), ("step", step), ("max_value", max_value)):
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError("%s must be a whole number, got %r." % (name, v))
    if run_index < 0:
        raise ValueError("run_index must be 0 or more, got %d." % run_index)
    raw = step * run_index
    if not wrap:
        return start + raw
    if max_value < start:
        raise ValueError("max_value (%d) is below start (%d). Raise max_value or turn wrap off." % (max_value, start))
    return start + raw % (max_value - start + 1)


class SYCounter:
    DESCRIPTION = "Counts up by a step on each run. You feed it the run number, so the same number always gives the same answer."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "run_index": ("INT", {"default": 0, "min": 0, "max": LIMIT, "tooltip": "Which run this is, from 0. Connect a batch index or a run counter."}),
                "start": ("INT", {"default": 0, "min": -LIMIT, "max": LIMIT, "tooltip": "The value on run 0."}),
                "step": ("INT", {"default": 1, "min": -LIMIT, "max": LIMIT, "tooltip": "How much the value changes on each run. Can be negative."}),
                "max_value": ("INT", {"default": 9, "min": -LIMIT, "max": LIMIT, "tooltip": "Highest value before it starts over at start. Used only when wrap is on."}),
                "wrap": ("BOOLEAN", {"default": True, "tooltip": "On starts over at start after max_value. Off keeps counting."}),
            }
        }

    def run(self, run_index, start, step, max_value, wrap):
        return (counter_value(run_index, start, step, max_value, wrap),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Counter", SYCounter)
