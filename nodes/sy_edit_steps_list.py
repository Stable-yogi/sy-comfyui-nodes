"""Edit Steps List SY: joins up to five edit steps into one numbered list, bullet list or sentence chain."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

import re

STYLES = ("numbered", "bullets", "then_words", "one_line")
MAX_STEPS = 8
_MARKER = re.compile(r"^\s*(?:\d{1,3}\s*[.)]|[-*•])(?:\s+|$)")


def strip_marker(step):
    """Pure function. Removes a list number or bullet the user already typed ('2. Fix it' becomes 'Fix it')."""
    return _MARKER.sub("", step, count=1).strip()


def clean_steps(steps, skip_duplicates=False):
    """Pure function. Steps without empty ones, typed numbers or bullets, and (optionally) repeats."""
    filled = [strip_marker(" ".join(str(s or "").split())) for s in steps]
    filled = [s for s in filled if s]
    if skip_duplicates:
        seen = set()
        unique = []
        for s in filled:
            key = s.lower().rstrip(".")
            if key not in seen:
                seen.add(key)
                unique.append(s)
        filled = unique
    return filled


def build_steps(steps, style, skip_duplicates=False):
    """Pure function. Empty steps are skipped; order is kept. A number or bullet already typed in a step is removed."""
    if style not in STYLES:
        raise ValueError("unknown style %r: choose one of %s" % (style, ", ".join(STYLES)))
    filled = clean_steps(steps, skip_duplicates)
    if not filled:
        raise ValueError("no step is filled: write at least one of step_1 to step_%d" % MAX_STEPS)
    if style == "numbered":
        return "\n".join("%d. %s" % (i, s) for i, s in enumerate(filled, start=1))
    if style == "bullets":
        return "\n".join("- " + s for s in filled)
    if style == "one_line":
        return "; ".join(s.rstrip(".") for s in filled) + "."
    out = []
    for i, s in enumerate(filled):
        s = s.rstrip(".")
        if i == 0:
            word = "First"
        elif i == len(filled) - 1:
            word = "Finally"
        else:
            word = "Then"
        out.append("%s, %s." % (word, s[:1].lower() + s[1:]))
    return " ".join(out)


class SYEditStepsList:
    DESCRIPTION = ("Joins up to eight edit steps into one list for an image edit model: numbered, bullets, First/Then/Finally or one line. "
                   "Empty steps are skipped, the order is kept, a number you already typed is not doubled, and repeats can be dropped. "
                   "Also gives the step count.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("steps", "count")

    @classmethod
    def INPUT_TYPES(cls):
        optional = {}
        for i in range(1, MAX_STEPS + 1):
            optional["step_%d" % i] = ("STRING", {"default": "", "tooltip": "Edit step number %d. Leave empty to skip it." % i})
        optional["skip_duplicates"] = ("BOOLEAN", {"default": False, "tooltip": "On: a step written twice is used once (capitals ignored)."})
        return {
            "required": {
                "style": (list(STYLES), {"default": "numbered", "tooltip": "How to write the list: numbers, bullets, First/Then/Finally, or one line with semicolons."}),
            },
            "optional": optional,
        }

    def run(self, style, step_1="", step_2="", step_3="", step_4="", step_5="", step_6="", step_7="", step_8="", skip_duplicates=False):
        steps = [step_1, step_2, step_3, step_4, step_5, step_6, step_7, step_8]
        return (build_steps(steps, style, skip_duplicates), len(clean_steps(steps, skip_duplicates)))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EditStepsList", SYEditStepsList)
