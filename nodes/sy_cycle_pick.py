"""Cycle Pick SY: picks one line from a list by a counter, going round and round."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def parse_items(items):
    """Pure function. One item per line, blank lines skipped, edges trimmed."""
    return [line.strip() for line in str(items).splitlines() if line.strip()]


def cycle_pick(items, counter):
    """Pure function. Returns (item, index, count)."""
    lines = parse_items(items)
    if not lines:
        raise ValueError("items is empty: type at least one line of text")
    idx = int(counter) % len(lines)
    return lines[idx], idx, len(lines)


class SYCyclePick:
    DESCRIPTION = "Picks one line from a list using a counter. When the counter passes the end it starts again from the first line."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("item", "index", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "items": ("STRING", {"default": "", "multiline": True, "tooltip": "One item per line. Blank lines are skipped."}),
                "counter": ("INT", {"default": 0, "min": -(2 ** 31), "max": 2 ** 31 - 1, "tooltip": "Which item to take, counting from 0. It goes round when too big."}),
            }
        }

    def run(self, items, counter):
        return cycle_pick(items, counter)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CyclePick", SYCyclePick)
