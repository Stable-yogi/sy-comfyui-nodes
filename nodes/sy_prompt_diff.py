"""Prompt Diff SY: compares the tags of two prompts and shows what is only in one and what they share."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

import re

MAX_INPUT = 2000000
_WRAP = re.compile(r"^[\(\[]+\s*(.*?)\s*(?::\s*[-+]?\d*\.?\d+\s*)?[\)\]]+$", re.S)


def _key(tag, ignore_weights=False):
    if ignore_weights:
        m = _WRAP.match(tag)
        if m and m.group(1):
            tag = m.group(1)
    return " ".join(tag.split()).lower()


def split_tags(text, separator=",", ignore_weights=False):
    """Pure function. Splits to trimmed, non-empty tags in order, with repeats (ignoring case) removed."""
    text = "" if text is None else str(text)
    if len(text) > MAX_INPUT:
        raise ValueError("text is too long: %d characters (limit %d)" % (len(text), MAX_INPUT))
    if separator is None or separator == "":
        raise ValueError("separator is empty: type the character that splits the tags, for example a comma")
    seen = set()
    tags = []
    for part in text.split(separator):
        tag = part.strip()
        if tag and _key(tag, ignore_weights) not in seen:
            seen.add(_key(tag, ignore_weights))
            tags.append(tag)
    return tags


def prompt_diff(text_a, text_b, separator=",", ignore_weights=False):
    """Pure function. Returns (only_in_a, only_in_b, shared) as lists of tags.
    ignore_weights makes (cat:1.2) and [cat] count as cat. Shared tags are written the way A wrote them."""
    a = split_tags(text_a, separator, ignore_weights)
    b = split_tags(text_b, separator, ignore_weights)
    keys_a = {_key(t, ignore_weights) for t in a}
    keys_b = {_key(t, ignore_weights) for t in b}
    only_a = [t for t in a if _key(t, ignore_weights) not in keys_b]
    only_b = [t for t in b if _key(t, ignore_weights) not in keys_a]
    shared = [t for t in a if _key(t, ignore_weights) in keys_b]
    return only_a, only_b, shared


def diff_summary(only_a, only_b, shared):
    """Pure function. Returns (similarity 0..1, plain info line). Similarity is shared tags divided by all different tags."""
    total = len(only_a) + len(only_b) + len(shared)
    sim = round(len(shared) / total, 3) if total else 1.0

    def s(n):
        return "tag" if n == 1 else "tags"

    na, nb = len(only_a) + len(shared), len(only_b) + len(shared)
    info = "A has %d %s, B has %d %s; %d shared (%d%% alike), %d only in A, %d only in B." % (
        na, s(na), nb, s(nb), len(shared), round(sim * 100), len(only_a), len(only_b))
    return sim, info


class SYPromptDiff:
    DESCRIPTION = ("Compares the tags of two prompts. Gives the tags only in A, only in B and shared by both, with counts, "
                   "a similarity number from 0 to 1 and a plain summary. Can ignore weights, so (cat:1.2) matches cat.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT", "INT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("only_in_a", "only_in_b", "shared", "count_only_a", "count_only_b", "count_shared", "similarity", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_a": ("STRING", {"default": "", "multiline": True, "tooltip": "The first prompt."}),
                "text_b": ("STRING", {"default": "", "multiline": True, "tooltip": "The second prompt to compare with the first."}),
                "separator": ("STRING", {"default": ",", "tooltip": "The character that splits one tag from the next."}),
            },
            "optional": {
                "ignore_weights": ("BOOLEAN", {"default": False, "tooltip": "On: (cat:1.2), [cat] and cat count as the same tag."}),
            },
        }

    def run(self, text_a, text_b, separator=",", ignore_weights=False):
        only_a, only_b, shared = prompt_diff(text_a, text_b, separator, ignore_weights)
        sim, info = diff_summary(only_a, only_b, shared)
        return (", ".join(only_a), ", ".join(only_b), ", ".join(shared), len(only_a), len(only_b), len(shared), sim, info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptDiff", SYPromptDiff)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptDiff"] = "Prompt Diff SY"
