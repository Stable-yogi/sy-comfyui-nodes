"""Seed Stepper SY: makes a row of seeds by adding a step, and picks the one at an index."""

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 64 - 1


def seed_at(base_seed, step, position):
    """Pure function. base + step * position, kept inside 0..MAX_SEED."""
    return (int(base_seed) + int(step) * int(position)) % (MAX_SEED + 1)


def step_seeds(base_seed, step, count, index, wrap=True):
    """Pure function. Returns (seed at index, list of all seeds)."""
    count = int(count)
    index = int(index)
    if count < 1:
        raise ValueError("count must be at least 1")
    if index < 0:
        raise ValueError("index must be 0 or more")
    if index >= count:
        if not wrap:
            raise ValueError("index %d is outside the list of %d seeds - lower index or turn wrap on" % (index, count))
        index = index % count
    seeds = [seed_at(base_seed, step, i) for i in range(count)]
    return seeds[index], seeds


class SYSeedStepper:
    DESCRIPTION = "Builds a list of seeds (base, base+step, base+2*step...) and gives the seed at one index, plus the whole list."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("seed", "seed_list")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "tooltip": "The first seed of the list."}),
                "step": ("INT", {"default": 1, "min": -1000000, "max": 1000000, "tooltip": "What is added to the seed for each next place."}),
                "count": ("INT", {"default": 4, "min": 1, "max": 256, "tooltip": "How many seeds are in the list."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Which place of the list to give out. 0 is the first."}),
                "wrap": ("BOOLEAN", {"default": True, "tooltip": "On: an index past the end starts over at the front. Off: that is an error."}),
            },
        }

    def run(self, base_seed, step, count, index, wrap=True):
        seed, seeds = step_seeds(base_seed, step, count, index, bool(wrap))
        return (seed, ", ".join(str(s) for s in seeds))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SeedStepper", SYSeedStepper)
NODE_DISPLAY_NAME_MAPPINGS["SYSeedStepper"] = "Seed Stepper SY"
