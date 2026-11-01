"""Tag Sort SY: sorts, shuffles or de-duplicates the tags of a prompt."""
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000
ORDERS = ("keep", "alphabetical", "shortest_first", "longest_first", "shuffle_seeded")


def tag_sort(text, separator=",", order="keep", seed=0, dedupe=True, trigger_first="", remove_tags=""):
    """Pure function. Returns the list of tags in the wanted order.
    trigger_first: tags that must stand first in this order (added if missing). remove_tags: tags to delete."""
    return tag_sort_full(text, separator, order, seed, dedupe, trigger_first, remove_tags)[0]


def _split_list(value, separator):
    value = "" if value is None else str(value)
    return [p.strip() for p in value.replace("\n", separator).split(separator) if p.strip()]


def tag_sort_full(text, separator=",", order="keep", seed=0, dedupe=True, trigger_first="", remove_tags=""):
    """Pure function. Returns (tags, stats) where stats counts what was removed, repeated, moved or added."""
    text = "" if text is None else str(text)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    if separator is None or separator == "":
        raise ValueError("separator is empty: type the character that splits the tags, for example a comma")
    if order not in ORDERS:
        raise ValueError("unknown order %r: choose one of %s" % (order, ", ".join(ORDERS)))
    tags = [p.strip() for p in text.split(separator)]
    tags = [t for t in tags if t]
    stats = {"removed": 0, "duplicates": 0, "pinned_moved": 0, "pinned_added": 0, "total": len(tags)}
    drop = {t.lower() for t in _split_list(remove_tags, separator)}
    if drop:
        kept = [t for t in tags if t.lower() not in drop]
        stats["removed"] = len(tags) - len(kept)
        tags = kept
    pins = []
    for t in _split_list(trigger_first, separator):
        if t.lower() not in [p.lower() for p in pins]:
            pins.append(t)
    pin_keys = {p.lower() for p in pins}
    present = {t.lower() for t in tags}
    for p in pins:
        if p.lower() in present:
            stats["pinned_moved"] += 1
        else:
            stats["pinned_added"] += 1
    if pins:
        before = len(tags)
        tags = [t for t in tags if t.lower() not in pin_keys]
        stats["duplicates"] += before - len(tags) - stats["pinned_moved"]
    before = len(tags)
    if dedupe:
        seen = set()
        unique = []
        for t in tags:
            if t.lower() not in seen:
                seen.add(t.lower())
                unique.append(t)
        tags = unique
    stats["duplicates"] += before - len(tags)
    if order == "alphabetical":
        tags.sort(key=lambda t: t.lower())
    elif order == "shortest_first":
        tags.sort(key=len)
    elif order == "longest_first":
        tags.sort(key=len, reverse=True)
    elif order == "shuffle_seeded":
        random.Random(int(seed)).shuffle(tags)
    return pins + tags, stats


def sort_info(stats, order, kept):
    """Pure function. One plain line telling what happened to the tags."""
    line = "%d tag(s) out (from %d), order: %s" % (kept, stats["total"], order)
    bits = []
    if stats["duplicates"]:
        bits.append("%d repeated removed" % stats["duplicates"])
    if stats["removed"]:
        bits.append("%d unwanted removed" % stats["removed"])
    if stats["pinned_moved"]:
        bits.append("%d moved to the front" % stats["pinned_moved"])
    if stats["pinned_added"]:
        bits.append("%d was missing and added at the front" % stats["pinned_added"])
    return line + ("; " + ", ".join(bits) if bits else "")


class SYTagSort:
    DESCRIPTION = ("Splits a prompt into tags, then sorts them (A to Z, by length, or a repeatable shuffle) and removes repeats. "
                   "For training captions it can keep the trigger word first (added if missing) and delete unwanted tags.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "The prompt whose tags you want to sort."}),
                "separator": ("STRING", {"default": ",", "tooltip": "The character that splits one tag from the next."}),
                "order": (list(ORDERS), {"default": "keep", "tooltip": "keep = same order. Others sort A to Z, by length, or shuffle the same way every time."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2 ** 63 - 1, "tooltip": "Number for the shuffle. The same number gives the same order."}),
                "dedupe": ("BOOLEAN", {"default": True, "tooltip": "On: remove tags that appear twice (capital letters are ignored)."}),
            },
            "optional": {
                "trigger_first": ("STRING", {"default": "", "tooltip": "Tags that must come first, in this order, for example 'ohwx'. Added when missing."}),
                "remove_tags": ("STRING", {"default": "", "tooltip": "Tags to delete, separated by commas, for example 'watermark, text'. Capital letters are ignored."}),
            },
        }

    def run(self, text, separator=",", order="keep", seed=0, dedupe=True, trigger_first="", remove_tags=""):
        tags, stats = tag_sort_full(text, separator, order, seed, dedupe, trigger_first, remove_tags)
        return (", ".join(tags), sort_info(stats, order, len(tags)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TagSort", SYTagSort)
NODE_DISPLAY_NAME_MAPPINGS["SYTagSort"] = "Tag Sort SY"
