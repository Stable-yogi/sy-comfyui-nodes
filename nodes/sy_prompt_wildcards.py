"""Prompt Choice SY: pick one option from each {a|b|c} group with a seeded random, same in browser and API runs."""
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 64 - 1
_ESCAPABLE = "{}|\\"


def expand_choices(text, seed):
    """Pure function. Replaces each {a|b|c} group with one option picked by random.Random(seed).
    A backslash before { } | or a backslash keeps that character literal. Nested groups are not supported:
    a { inside a group is plain text. A group that never closes stays literal."""
    text = "" if text is None else str(text)
    rng = random.Random(max(0, min(int(seed), MAX_SEED)))
    out = []
    n = len(text)
    i = 0
    while i < n:
        ch = text[i]
        if ch == "\\" and i + 1 < n and text[i + 1] in _ESCAPABLE:
            out.append(text[i + 1])
            i += 2
            continue
        if ch != "{":
            out.append(ch)
            i += 1
            continue
        options = []
        cur = []
        j = i + 1
        closed = False
        while j < n:
            c = text[j]
            if c == "\\" and j + 1 < n and text[j + 1] in _ESCAPABLE:
                cur.append(text[j + 1])
                j += 2
                continue
            if c == "|":
                options.append("".join(cur))
                cur = []
            elif c == "}":
                options.append("".join(cur))
                closed = True
                break
            else:
                cur.append(c)
            j += 1
        if not closed:
            out.append("{")
            i += 1
            continue
        out.append(rng.choice(options))
        i = j + 1
    return "".join(out)


class SYPromptChoice:
    DESCRIPTION = "Picks one option from each {red|green|blue} group in the text. The same seed gives the same result in the browser and in an API run. Use a backslash before a brace to keep it literal."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED}),
            }
        }

    def run(self, text, seed):
        return (expand_choices(text, seed),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptChoice", SYPromptChoice)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptChoice"] = "Prompt Choice SY"
