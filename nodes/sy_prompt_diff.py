"""Prompt Diff SY: compares the tags of two prompts and shows what is only in one and what they share."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_INPUT = 2000000


def split_tags(text, separator=","):
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
        if tag and tag.lower() not in seen:
            seen.add(tag.lower())
            tags.append(tag)
    return tags


def prompt_diff(text_a, text_b, separator=","):
    """Pure function. Returns (only_in_a, only_in_b, shared) as lists of tags."""
    a = split_tags(text_a, separator)
    b = split_tags(text_b, separator)
    keys_a = {t.lower() for t in a}
    keys_b = {t.lower() for t in b}
    only_a = [t for t in a if t.lower() not in keys_b]
    only_b = [t for t in b if t.lower() not in keys_a]
    shared = [t for t in a if t.lower() in keys_b]
    return only_a, only_b, shared


class SYPromptDiff:
    DESCRIPTION = "Compares the tags of two prompts. Gives the tags only in A, only in B and shared by both, with counts."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT", "INT", "INT")
    RETURN_NAMES = ("only_in_a", "only_in_b", "shared", "count_only_a", "count_only_b", "count_shared")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_a": ("STRING", {"default": "", "multiline": True, "tooltip": "The first prompt."}),
                "text_b": ("STRING", {"default": "", "multiline": True, "tooltip": "The second prompt to compare with the first."}),
                "separator": ("STRING", {"default": ",", "tooltip": "The character that splits one tag from the next."}),
            }
        }

    def run(self, text_a, text_b, separator=","):
        only_a, only_b, shared = prompt_diff(text_a, text_b, separator)
        return (", ".join(only_a), ", ".join(only_b), ", ".join(shared), len(only_a), len(only_b), len(shared))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptDiff", SYPromptDiff)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptDiff"] = "Prompt Diff SY"
