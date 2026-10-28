"""Random Choice SY: picks one line from a list of lines, the same pick for the same seed."""
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 64 - 1


def pick_line(text, seed):
    """Pure function. Returns (chosen line, index among the non-empty lines)."""
    lines = [ln.strip() for ln in str(text).splitlines() if ln.strip()]
    if not lines:
        raise ValueError("lines is empty - type at least one line of text")
    index = random.Random(int(seed)).randrange(len(lines))
    return lines[index], index


class SYRandomChoice:
    DESCRIPTION = "Picks one line out of your list of lines. The same seed always picks the same line."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("chosen", "index")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lines": ("STRING", {"default": "", "multiline": True, "tooltip": "One choice per line. Empty lines are skipped."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "tooltip": "Decides the pick. Change it to get another line."}),
            },
        }

    def run(self, lines, seed):
        return pick_line(lines, seed)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RandomChoice", SYRandomChoice)
NODE_DISPLAY_NAME_MAPPINGS["SYRandomChoice"] = "Random Choice SY"
