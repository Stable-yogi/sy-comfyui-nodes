"""Cycle Pick SY: picks one line from a list by a counter, going round and round."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


MODES = ("loop", "ping-pong", "stop at last")


def parse_items(items, skip_comments=False):
    """Pure function. One item per line, blank lines skipped, edges trimmed.
    With skip_comments on, lines that start with # are skipped too."""
    lines = [line.strip() for line in str(items).splitlines() if line.strip()]
    if skip_comments:
        lines = [line for line in lines if not line.startswith("#")]
    return lines


def pick_index(counter, count, mode="loop"):
    """Pure function. Turns a counter into a position 0..count-1.
    loop: 0 1 2 0 1 2. ping-pong: 0 1 2 1 0 1 2. stop at last: 0 1 2 2 2 (negative numbers stay on the first)."""
    if mode not in MODES:
        raise ValueError("mode must be one of %s, got %r." % (", ".join(MODES), mode))
    if mode == "stop at last":
        return min(max(counter, 0), count - 1)
    if mode == "ping-pong" and count > 1:
        period = 2 * count - 2
        pos = counter % period
        return pos if pos < count else period - pos
    return counter % count


def cycle_pick(items, counter, mode="loop", skip_comments=False):
    """Pure function. Returns (item, index, count)."""
    if isinstance(counter, bool) or not isinstance(counter, (int, float)) or counter != counter:
        raise ValueError("counter must be a whole number, got %r." % (counter,))
    lines = parse_items(items, skip_comments)
    if not lines:
        raise ValueError("items is empty: type at least one line of text%s" % (" (lines starting with # are skipped)" if skip_comments else ""))
    idx = pick_index(int(counter), len(lines), mode)
    return lines[idx], idx, len(lines)


def pick_info(index, count, counter, mode="loop"):
    """Pure function. A plain line saying which item came out and why."""
    note = ""
    if int(counter) != index:
        if mode == "stop at last":
            note = " (counter %d is past the end, so it stays on the last)" % int(counter)
        else:
            note = " (counter %d went round)" % int(counter)
    return "Item %d of %d, mode %s%s." % (index + 1, count, mode, note)


class SYCyclePick:
    DESCRIPTION = "Picks one line from a list using a counter. When the counter passes the end it starts again from the first line, or bounces back (ping-pong), or stays on the last. Can skip # comment lines."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("item", "index", "count", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "items": ("STRING", {"default": "", "multiline": True, "tooltip": "One item per line. Blank lines are skipped."}),
                "counter": ("INT", {"default": 0, "min": -(2 ** 31), "max": 2 ** 31 - 1, "tooltip": "Which item to take, counting from 0. It goes round when too big."}),
            },
            "optional": {
                "mode": (list(MODES), {"default": "loop", "tooltip": "loop: 0 1 2 0 1 2. ping-pong: 0 1 2 1 0 1. stop at last: 0 1 2 2 2."}),
                "skip_comments": ("BOOLEAN", {"default": False, "tooltip": "On skips lines that start with #, so you can switch items off."}),
            },
        }

    def run(self, items, counter, mode="loop", skip_comments=False):
        item, idx, count = cycle_pick(items, counter, mode, skip_comments)
        return (item, idx, count, pick_info(idx, count, counter, mode))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CyclePick", SYCyclePick)
