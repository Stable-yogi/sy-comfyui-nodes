"""Seed SY: a seed with fixed / random / increment modes that works in headless (API) runs."""
import secrets

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 64 - 1
MODES = ("fixed", "random", "increment")
SEED_RANGES = ("64-bit", "53-bit (browser safe)", "32-bit")
_RANGE_MAX = {"64-bit": MAX_SEED, "53-bit (browser safe)": 2 ** 53 - 1, "32-bit": 2 ** 32 - 1}
_counters = {}  # unique_id -> last seed used in increment mode


def resolve_seed(seed, mode, last=None, seed_range="64-bit"):
    """Pure function. Returns the seed to use for this run. seed_range limits how big a seed can get."""
    if seed_range not in _RANGE_MAX:
        raise ValueError("seed_range must be one of: %s, got %r" % (", ".join(SEED_RANGES), seed_range))
    top = _RANGE_MAX[seed_range]
    seed = max(0, min(int(seed), top))
    if mode == "fixed":
        return seed
    if mode == "random":
        return secrets.randbelow(top + 1)
    if mode == "increment":
        if last is None:
            return seed
        return (last + 1) % (top + 1)
    raise ValueError("unknown seed mode: %r" % (mode,))


def seed_info(requested, used, mode, seed_range="64-bit"):
    """Pure function. Returns (text, info): the seed as text for file names, and one plain line."""
    info = "seed %d (%s, %s range)" % (used, mode, seed_range)
    if mode == "fixed" and int(requested) != used:
        info += ", the typed number did not fit this range and was changed"
    return str(used), info


class SYSeed:
    DESCRIPTION = "Gives one seed number. Fixed keeps it. Random picks a new one each run. Increment adds 1 each run. Also gives the seed as text (for file names) and an info line, and can limit the seed to 53-bit or 32-bit so it is never too big for the browser or an older node."
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "STRING", "STRING")
    RETURN_NAMES = ("seed", "text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "tooltip": "The seed number. Same number gives the same picture."}),
                "mode": (list(MODES), {"default": "fixed", "tooltip": "Fixed keeps the number. Random picks a new one each run. Increment adds 1 each run."}),
            },
            "optional": {
                "seed_range": (list(SEED_RANGES), {"default": "64-bit", "tooltip": "Biggest seed allowed. Pick 53-bit if a seed loses digits in the browser, 32-bit for older nodes."}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    @classmethod
    def IS_CHANGED(cls, seed, mode, unique_id=None, seed_range="64-bit"):
        # random and increment must re-run every time
        return float("nan") if mode != "fixed" else "%s:%s" % (seed, seed_range)

    def run(self, seed, mode, unique_id=None, seed_range="64-bit"):
        used = resolve_seed(seed, mode, _counters.get(unique_id), seed_range)
        _counters[unique_id] = used
        text, info = seed_info(seed, used, mode, seed_range)
        return (used, text, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Seed", SYSeed)
