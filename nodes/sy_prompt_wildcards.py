"""Prompt Choice SY: pick one option from each {a|b|c} group with a seeded random, same in browser and API runs."""
import random

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_SEED = 2 ** 64 - 1
_ESCAPABLE = "{}|\\"


def expand_choices(text, seed, trim_options=False):
    """Pure function. Replaces each {a|b|c} group with one option picked by random.Random(seed).
    A backslash before { } | or a backslash keeps that character literal. Nested groups are not supported:
    a { inside a group is plain text. A group that never closes stays literal. trim_options removes spaces around options."""
    return expand_choices_info(text, seed, trim_options)[0]


def expand_choices_info(text, seed, trim_options=False):
    """Pure function. Same as expand_choices but returns (text, picks, unclosed_count). picks lists what each group chose."""
    text = "" if text is None else str(text)
    rng = random.Random(max(0, min(int(seed), MAX_SEED)))
    out = []
    picks = []
    unclosed = 0
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
            unclosed += 1
            i += 1
            continue
        chosen = rng.choice(options)
        if trim_options:
            chosen = chosen.strip()
        picks.append(chosen)
        out.append(chosen)
        i = j + 1
    return "".join(out), picks, unclosed


def choice_info(picks, unclosed, seed):
    """Pure function. One plain line telling what each group picked."""
    if not picks and not unclosed:
        return "No {a|b} groups found in the text, so nothing was changed"
    shown = ", ".join(repr(p) if p else "(nothing)" for p in picks[:12])
    if len(picks) > 12:
        shown += ", ... (%d more)" % (len(picks) - 12)
    line = "Seed %d picked %d group(s)" % (max(0, min(int(seed), MAX_SEED)), len(picks))
    if picks:
        line += ": " + shown
    if unclosed:
        line += "; WARNING: %d '{' has no closing '}' and was kept as plain text (use \\{ for a real brace)" % unclosed
    return line


class SYPromptChoice:
    DESCRIPTION = ("Picks one option from each {red|green|blue} group in the text. The same seed gives the same result in the browser and in an API run. "
                   "Use a backslash before a brace to keep it literal. The info line shows what each group picked and warns about a missing closing brace.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True, "tooltip": "Your prompt. Write {red|blue} to pick one option at random."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": MAX_SEED, "tooltip": "Same number gives the same picks every time. Change it to get other picks."}),
            },
            "optional": {
                "trim_options": ("BOOLEAN", {"default": False, "tooltip": "On: spaces around an option are removed, so { red | blue } gives red or blue."}),
            },
        }

    def run(self, text, seed, trim_options=False):
        out, picks, unclosed = expand_choices_info(text, seed, trim_options)
        return (out, choice_info(picks, unclosed, seed))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "PromptChoice", SYPromptChoice)
NODE_DISPLAY_NAME_MAPPINGS["SYPromptChoice"] = "Prompt Choice SY"
