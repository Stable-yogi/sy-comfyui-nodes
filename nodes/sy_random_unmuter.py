"""Random Unmuter SY: before every run it switches ON one node out of a set and switches the others OFF.
The switching happens in the browser (js/sy_random_unmuter.js). This file holds the node shell and the plain rules
(the same rules are in js/sy_random_unmuter_logic.js), so they can be tested."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

PICKS = ("random", "round_robin")
OFF_MODES = ("Mute", "Bypass")
MAX_SEED = 2 ** 31 - 1
_M = 0xFFFFFFFF


def split_words(text):
    """Pure function. 'a, b ,,C' gives ['a', 'b', 'c'] (lower case, no empty words, no repeats, order kept)."""
    out = []
    for w in str(text or "").split(","):
        w = w.strip().lower()
        if w and w not in out:
            out.append(w)
    return out


def match_titles(titles, title_filter):
    """Pure function. Positions of the titles that contain ANY word of the filter (case does not matter).
    An empty filter matches nothing, so nothing is ever switched by accident."""
    words = split_words(title_filter)
    if not words:
        return []
    return [i for i, t in enumerate(titles) if any(w in str(t or "").lower() for w in words)]


def mix32(seed, counter):
    """Pure function. A fixed 32-bit mix of seed and counter, same result in Python and JavaScript."""
    h = ((int(counter) + 1) * 0x9E3779B1) & _M
    h = (h ^ (int(seed) & _M)) & _M
    h = ((h ^ (h >> 16)) * 0x85EBCA6B) & _M
    h = ((h ^ (h >> 13)) * 0xC2B2AE35) & _M
    return (h ^ (h >> 16)) & _M


def pick_index(count, pick, seed, counter, rand=0.0):
    """Pure function. Which of `count` candidates is ON for this run, or -1 when there are none.
    round_robin: counter % count. random with seed 0: from rand (0 <= rand < 1, supplied by the caller).
    random with a seed: the same seed and counter always give the same answer."""
    count = int(count)
    if count <= 0:
        return -1
    if pick == "round_robin":
        return int(counter) % count
    if int(seed) == 0:
        return min(count - 1, max(0, int(float(rand) * count)))
    return mix32(seed, counter) % count


def plan_modes(count, on_index, off_mode):
    """Pure function. The LiteGraph mode number for each candidate: 0 for the chosen one, 2 (mute) or 4 (bypass) for the rest."""
    off = 4 if str(off_mode).lower() == "bypass" else 2
    return [0 if i == on_index else off for i in range(int(count))]


class SYRandomUnmuter:
    DESCRIPTION = ("Before each run it switches ON one node out of a set and switches the rest OFF, so every run uses a different one. "
                   "The set is every node whose title holds one of your words. Pick at random or one after the other. It has no wires.")
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ()
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "title_filter": ("STRING", {"default": "", "multiline": False, "tooltip": "Words separated by commas. Every node whose title holds one of them is in the set. Rename nodes to group them."}),
                "pick": (list(PICKS), {"default": "random", "tooltip": "random picks any one. round_robin goes through the set one by one."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "tooltip": "0 picks differently every time. Any other number gives the same order again and again."}),
                "off_mode": (list(OFF_MODES), {"default": "Mute", "tooltip": "What happens to the nodes that are not picked. Mute stops them. Bypass lets the picture pass through."}),
                "enabled": ("BOOLEAN", {"default": True, "tooltip": "Off leaves your nodes exactly as they are."}),
            }
        }

    def run(self, title_filter="", pick="random", seed=0, off_mode="Mute", enabled=True):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RandomUnmuter", SYRandomUnmuter)
