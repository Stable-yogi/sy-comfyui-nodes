"""Random In Range SY: a random whole number and a random decimal between two limits. The same seed gives the same numbers."""
import math
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

SEED_MAX = 2 ** 64 - 1


def random_in_range(seed, min_value, max_value):
    """Pure function. Returns (int, float). Both limits are included for the whole number."""
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a whole number from 0 up, got %r." % (seed,))
    for name, v in (("min_value", min_value), ("max_value", max_value)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError("%s must be a normal number, got %r." % (name, v))
    if min_value > max_value:
        raise ValueError("min_value (%g) is bigger than max_value (%g). Swap them." % (min_value, max_value))
    rng = random.Random(seed)
    f = min_value + rng.random() * (max_value - min_value)
    f = min(max(f, min_value), max_value)
    lo, hi = math.ceil(min_value), math.floor(max_value)
    if lo > hi:  # no whole number fits inside, so give the nearest one to the decimal
        i = int(math.floor(f + 0.5))
    else:
        i = rng.randint(lo, hi)
    return i, float(f)


class SYRandomInRange:
    DESCRIPTION = "Makes a random whole number and a random decimal between two limits. The same seed always gives the same answer."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("int", "float")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": SEED_MAX, "tooltip": "Same seed, same numbers. Change it for new numbers."}),
                "min_value": ("FLOAT", {"default": 0.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": "Lowest number that can come out."}),
                "max_value": ("FLOAT", {"default": 100.0, "min": -1e15, "max": 1e15, "step": 0.01, "tooltip": "Highest number that can come out. Not below min_value."}),
            }
        }

    def run(self, seed, min_value, max_value):
        return random_in_range(seed, min_value, max_value)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RandomInRange", SYRandomInRange)
NODE_DISPLAY_NAME_MAPPINGS["SYRandomInRange"] = "Random In Range SY"
