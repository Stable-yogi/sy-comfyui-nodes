"""Seed SY: a seed with fixed / random / increment modes that works in headless (API) runs."""
import secrets

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 64 - 1
MODES = ("fixed", "random", "increment")
_counters = {}  # unique_id -> last seed used in increment mode


def resolve_seed(seed, mode, last=None):
    """Pure function. Returns the seed to use for this run."""
    seed = max(0, min(int(seed), MAX_SEED))
    if mode == "fixed":
        return seed
    if mode == "random":
        return secrets.randbelow(MAX_SEED + 1)
    if mode == "increment":
        if last is None:
            return seed
        return (last + 1) % (MAX_SEED + 1)
    raise ValueError("unknown seed mode: %r" % (mode,))


class SYSeed:
    DESCRIPTION = "Gives one seed number. Fixed keeps it. Random picks a new one each run. Increment adds 1 each run."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED}),
                "mode": (list(MODES), {"default": "fixed"}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    @classmethod
    def IS_CHANGED(cls, seed, mode, unique_id=None):
        # random and increment must re-run every time
        return float("nan") if mode != "fixed" else seed

    def run(self, seed, mode, unique_id=None):
        used = resolve_seed(seed, mode, _counters.get(unique_id))
        _counters[unique_id] = used
        return (used,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Seed", SYSeed)
