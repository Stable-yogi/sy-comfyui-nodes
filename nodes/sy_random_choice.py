"""Random Choice SY: picks one line from a list of lines, the same pick for the same seed."""
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 64 - 1


PICK_MODES = ["random from seed", "in order (seed 0 = first line)"]


def clean_lines(text, skip_comments=False):
    """Pure function. The non-empty lines, trimmed. skip_comments drops lines that start with #."""
    lines = [ln.strip() for ln in str(text).splitlines() if ln.strip()]
    if skip_comments:
        lines = [ln for ln in lines if not ln.startswith("#")]
    return lines


def pick_line(text, seed, mode=PICK_MODES[0], skip_comments=False):
    """Pure function. Returns (chosen line, index among the non-empty lines).
    'in order' walks the list as the seed goes up and starts again at the end."""
    if mode not in PICK_MODES:
        raise ValueError("mode must be one of: %s" % ", ".join(PICK_MODES))
    lines = clean_lines(text, skip_comments)
    if not lines:
        raise ValueError("lines is empty - type at least one line of text" + (" (lines starting with # are skipped)" if skip_comments else ""))
    if mode == PICK_MODES[1]:
        index = int(seed) % len(lines)
    else:
        index = random.Random(int(seed)).randrange(len(lines))
    return lines[index], index


def pick_info(text, seed, mode=PICK_MODES[0], skip_comments=False):
    """Pure function. One plain line: which line of how many was picked."""
    count = len(clean_lines(text, skip_comments))
    chosen, index = pick_line(text, seed, mode, skip_comments)
    line = "Picked line %d of %d (seed %d, %s)" % (index + 1, count, int(seed), "in order" if mode == PICK_MODES[1] else "random")
    if count == 1:
        line += "; WARNING: only one line to choose from"
    return line


class SYRandomChoice:
    DESCRIPTION = ("Picks one line out of your list of lines. The same seed always picks the same line. Can instead walk the list in order "
                   "(seed 0, 1, 2 ...), skips # comment lines, and the info line says which line was picked.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("chosen", "index", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lines": ("STRING", {"default": "", "multiline": True, "tooltip": "One choice per line. Empty lines are skipped."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "tooltip": "Decides the pick. Change it to get another line."}),
            },
            "optional": {
                "mode": (PICK_MODES, {"default": PICK_MODES[0], "tooltip": "In order: seed 0 gives line 1, seed 1 gives line 2, and so on, then it starts over."}),
                "skip_comments": ("BOOLEAN", {"default": False, "tooltip": "On: lines that start with # are ignored."}),
            },
        }

    def run(self, lines, seed, mode=PICK_MODES[0], skip_comments=False):
        chosen, index = pick_line(lines, seed, mode, skip_comments)
        return (chosen, index, pick_info(lines, seed, mode, skip_comments))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "RandomChoice", SYRandomChoice)
NODE_DISPLAY_NAME_MAPPINGS["SYRandomChoice"] = "Random Choice SY"
