"""Random In Range SY: a random whole number and a random decimal between two limits. The same seed gives the same numbers."""
import math
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SEED_MAX = 2 ** 64 - 1


def random_in_range(seed, min_value, max_value, step=0.0):
    """Pure function. Returns (int, float). Both limits are included for the whole number.
    step above 0 puts the decimal on a grid of that size (for example 0.5) counted from min_value."""
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a whole number from 0 up, got %r." % (seed,))
    for name, v in (("min_value", min_value), ("max_value", max_value)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError("%s must be a normal number, got %r." % (name, v))
    if min_value > max_value:
        raise ValueError("min_value (%g) is bigger than max_value (%g). Swap them." % (min_value, max_value))
    if isinstance(step, bool) or not isinstance(step, (int, float)) or not math.isfinite(step) or step < 0:
        raise ValueError("step must be 0 or more, got %r. Use 0 for no grid." % (step,))
    rng = random.Random(seed)
    f = min_value + rng.random() * (max_value - min_value)
    f = min(max(f, min_value), max_value)
    if step > 0:
        f = min_value + round((f - min_value) / step) * step
        if f > max_value:
            f -= step
        f = round(min(max(f, min_value), max_value), 10)
    lo, hi = math.ceil(min_value), math.floor(max_value)
    if lo > hi:  # no whole number fits inside, so give the nearest one to the decimal
        i = int(math.floor(f + 0.5))
    else:
        i = rng.randint(lo, hi)
    return i, float(f)


def random_report(seed, min_value, max_value, step=0.0):
    """Pure function. Returns (int, float, info)."""
    i, f = random_in_range(seed, min_value, max_value, step)
    return i, f, "seed %d gives int %d and float %g (range %g to %g%s)" % (seed, i, f, min_value, max_value, ", step %g" % step if step else "")


class SYRandomInRange:
    DESCRIPTION = "Makes a random whole number and a random decimal between two limits. The same seed always gives the same answer. The optional step puts the decimal on a grid (like 0.5), and the info line tells what came out."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT", "STRING")
    RETURN_NAMES = ("int", "float", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": SEED_MAX, "tooltip": "Same seed, same numbers. Change it for new numbers."}),
                "min_value": ("FLOAT", {"default": 0.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": "Lowest number that can come out."}),
                "max_value": ("FLOAT", {"default": 100.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": "Highest number that can come out. Not below min_value."}),
            },
            "optional": {
                "step": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1e15, "step": 0.01, "tooltip": "0 is off. 0.5 makes the decimal land on 0.5 steps, like a CFG of 6.5."}),
            },
        }

    def run(self, seed, min_value, max_value, step=0.0):
        return random_report(seed, min_value, max_value, step)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RandomInRange", SYRandomInRange)
NODE_DISPLAY_NAME_MAPPINGS["SYRandomInRange"] = "Random In Range SY"
