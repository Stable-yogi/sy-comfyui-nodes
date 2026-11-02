"""Global Seed SY: one seed box that sets the seed of every other seed-taking node in the graph, with no wires.
The setting of the other nodes happens in the browser (js/sy_global_seed.js). This file holds the node shell and the plain rules
(the same rules are in js/sy_global_seed_logic.js), so they can be tested without a browser."""
import secrets

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 53 - 1  # the biggest whole number a browser keeps exact
MODES = ["fixed", "random", "increment", "decrement"]
SEED_NAMES = ("seed", "noise_seed", "rng_seed")


def is_seed_name(name):
    """True for the widget names that hold a seed."""
    return str(name or "").strip().lower() in SEED_NAMES


def clamp_seed(value):
    """A whole number from 0 up to MAX_SEED. Anything else becomes 0."""
    try:
        n = int(float(value))
    except (TypeError, ValueError, OverflowError):
        return 0
    return max(0, min(n, MAX_SEED))


def next_seed(seed, mode, rnd=None):
    """The seed for the NEXT run. rnd is a number from 0 up to (not including) 1; None takes a fresh random one."""
    s = clamp_seed(seed)
    m = str(mode or "").strip().lower()
    if m == "random":
        if rnd is None:
            return secrets.randbelow(MAX_SEED + 1)
        return min(MAX_SEED, int(float(rnd) * (MAX_SEED + 1)))
    if m == "increment":
        return 0 if s >= MAX_SEED else s + 1
    if m == "decrement":
        return MAX_SEED if s <= 0 else s - 1
    return s


def fit_seed(seed, top):
    """A target seed box can be smaller than ours. A bigger seed is folded into its range, a smaller one is kept."""
    s = clamp_seed(seed)
    try:
        t = int(top)
    except (TypeError, ValueError):
        return s
    if t < 0 or s <= t:
        return s
    return s % (t + 1)


def parse_words(text):
    """The skip words: comma separated, lower case, empty ones dropped."""
    return [w.strip().lower() for w in str(text or "").split(",") if w.strip()]


def skip_by_title(title, words):
    """True when the node title holds one of the skip words."""
    t = str(title or "").lower()
    return any(w and w in t for w in (words or []))


class SYGlobalSeed:
    DESCRIPTION = ("One seed for the whole graph. Before each run it writes this seed into every other node that has a seed box "
                   "(seed, noise_seed), with no wires. Then it picks the next seed by the mode. The seed also comes out of the node.")
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "control_after_generate": False, "tooltip": "The seed for the next run. It goes into every other seed box in the graph."}),
                "mode": (MODES, {"default": "fixed", "tooltip": "What happens after each run: fixed keeps the seed, random picks a new one, increment adds 1, decrement takes 1."}),
                "apply_to_all": ("BOOLEAN", {"default": True, "label_on": "on", "label_off": "off", "tooltip": "On writes the seed into the other seed boxes. Off leaves them alone (only the output is used)."}),
            },
            "optional": {
                "skip_titles": ("STRING", {"default": "", "multiline": False, "tooltip": "Nodes whose title holds one of these words (comma separated) keep their own seed."}),
            },
        }

    def run(self, seed, mode="fixed", apply_to_all=True, skip_titles=""):
        return (clamp_seed(seed),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "GlobalSeed", SYGlobalSeed)
NODE_DISPLAY_NAME_MAPPINGS["SYGlobalSeed"] = "Global Seed SY"
