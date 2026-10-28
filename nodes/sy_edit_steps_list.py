"""Edit Steps List SY: joins up to five edit steps into one numbered list, bullet list or sentence chain."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

STYLES = ("numbered", "bullets", "then_words")


def build_steps(steps, style):
    """Pure function. Empty steps are skipped; order is kept."""
    if style not in STYLES:
        raise ValueError("unknown style %r: choose one of %s" % (style, ", ".join(STYLES)))
    filled = [" ".join(str(s or "").split()) for s in steps]
    filled = [s for s in filled if s]
    if not filled:
        raise ValueError("no step is filled: write at least one of step_1 to step_5")
    if style == "numbered":
        return "\n".join("%d. %s" % (i, s) for i, s in enumerate(filled, start=1))
    if style == "bullets":
        return "\n".join("- " + s for s in filled)
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
    DESCRIPTION = "Joins up to five edit steps into one list for an image edit model. Empty steps are skipped and the order is kept."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("steps",)

    @classmethod
    def INPUT_TYPES(cls):
        optional = {}
        for i in range(1, 6):
            optional["step_%d" % i] = ("STRING", {"default": "", "tooltip": "Edit step number %d. Leave empty to skip it." % i})
        return {
            "required": {
                "style": (list(STYLES), {"default": "numbered", "tooltip": "How to write the list: numbers, bullets, or First, Then, Finally."}),
            },
            "optional": optional,
        }

    def run(self, style, step_1="", step_2="", step_3="", step_4="", step_5=""):
        return (build_steps([step_1, step_2, step_3, step_4, step_5], style),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EditStepsList", SYEditStepsList)
