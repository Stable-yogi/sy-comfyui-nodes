"""Seed List SY: makes a list of seeds, in a row or pseudo-random but the same every run."""
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 64 - 1
MODES = ("sequential", "random_fixed")


def make_seeds(base_seed, count, mode):
    """Pure function. Returns a list of `count` seeds."""
    count = int(count)
    base = max(0, min(int(base_seed), MAX_SEED))
    if not 1 <= count <= 64:
        raise ValueError("count must be between 1 and 64")
    if mode == "sequential":
        return [(base + i) % (MAX_SEED + 1) for i in range(count)]
    if mode == "random_fixed":
        rng = random.Random(base)
        return [rng.randrange(0, MAX_SEED + 1) for _ in range(count)]
    raise ValueError("unknown seed list mode %r - pick sequential or random_fixed" % (mode,))


class SYSeedList:
    DESCRIPTION = "Makes a comma list of seeds. Sequential counts up. Random fixed looks random but is the same every run."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("seed_list", "first_seed")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "tooltip": "Start number. Same start gives the same list."}),
                "count": ("INT", {"default": 4, "min": 1, "max": 64, "tooltip": "How many seeds to make (1 to 64)."}),
                "mode": (list(MODES), {"default": "sequential", "tooltip": "Sequential: base, base+1... Random fixed: scattered numbers, repeatable."}),
            },
        }

    def run(self, base_seed, count, mode):
        seeds = make_seeds(base_seed, count, mode)
        return (", ".join(str(s) for s in seeds), seeds[0])


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SeedList", SYSeedList)
NODE_DISPLAY_NAME_MAPPINGS["SYSeedList"] = "Seed List SY"
