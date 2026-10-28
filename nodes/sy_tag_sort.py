"""Tag Sort SY: sorts, shuffles or de-duplicates the tags of a prompt."""
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
ORDERS = ("keep", "alphabetical", "shortest_first", "longest_first", "shuffle_seeded")


def tag_sort(text, separator=",", order="keep", seed=0, dedupe=True):
    """Pure function. Returns the list of tags in the wanted order."""
    text = "" if text is None else str(text)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    if separator is None or separator == "":
        raise ValueError("separator is empty: type the character that splits the tags, for example a comma")
    if order not in ORDERS:
        raise ValueError("unknown order %r: choose one of %s" % (order, ", ".join(ORDERS)))
    tags = [p.strip() for p in text.split(separator)]
    tags = [t for t in tags if t]
    if dedupe:
        seen = set()
        unique = []
        for t in tags:
            if t.lower() not in seen:
                seen.add(t.lower())
                unique.append(t)
        tags = unique
    if order == "alphabetical":
        tags.sort(key=lambda t: t.lower())
    elif order == "shortest_first":
        tags.sort(key=len)
    elif order == "longest_first":
        tags.sort(key=len, reverse=True)
    elif order == "shuffle_seeded":
        random.Random(int(seed)).shuffle(tags)
    return tags


class SYTagSort:
    DESCRIPTION = "Splits a prompt into tags, then sorts them (A to Z, by length, or a repeatable shuffle) and removes repeats."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The prompt whose tags you want to sort."}),
                "separator": ("STRING", {"default": ",", "tooltip": "The character that splits one tag from the next."}),
                "order": (list(ORDERS), {"default": "keep", "tooltip": "keep = same order. Others sort A to Z, by length, or shuffle the same way every time."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 63 - 1, "tooltip": "Number for the shuffle. The same number gives the same order."}),
                "dedupe": ("BOOLEAN", {"default": True, "tooltip": "On: remove tags that appear twice (capital letters are ignored)."}),
            }
        }

    def run(self, text, separator=",", order="keep", seed=0, dedupe=True):
        return (", ".join(tag_sort(text, separator, order, seed, dedupe)),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TagSort", SYTagSort)
NODE_DISPLAY_NAME_MAPPINGS["SYTagSort"] = "Tag Sort SY"
