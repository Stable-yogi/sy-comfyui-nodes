"""Edit Instruction SY: builds one clear sentence that tells an image edit model what to change."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

ACTIONS = ("replace", "remove", "add", "recolour", "restyle", "change_background", "fix_lighting")
NEEDS_VALUE = ("replace", "add", "recolour", "restyle", "change_background")
KEEP_SENTENCE = "Keep everything else exactly the same."


def _clean(text):
    return " ".join(str(text or "").split()).strip().rstrip(".").strip()


def build_edit_instruction(action, target, to_value="", keep_rest=True, extra=""):
    """Pure function. Returns the instruction text."""
    if action not in ACTIONS:
        raise ValueError("unknown action %r: choose one of %s" % (action, ", ".join(ACTIONS)))
    t = _clean(target)
    v = _clean(to_value)
    if not t:
        raise ValueError("target is empty: say what part of the picture to change")
    if action in NEEDS_VALUE and not v:
        raise ValueError("to_value is empty: the action '%s' needs to know what to change it to" % action)
    if action == "replace":
        text = "Replace the %s with %s." % (t, v)
    elif action == "remove":
        text = "Remove the %s." % t
    elif action == "add":
        text = "Add %s to the %s." % (v, t)
    elif action == "recolour":
        text = "Change the colour of the %s to %s." % (t, v)
    elif action == "restyle":
        text = "Change the style of the %s to %s." % (t, v)
    elif action == "change_background":
        text = "Change the background behind the %s to %s." % (t, v)
    else:
        text = "Fix the lighting on the %s." % t
    e = _clean(extra)
    if e:
        text += " " + e + "."
    if keep_rest:
        text += " " + KEEP_SENTENCE
    return text


class SYEditInstruction:
    DESCRIPTION = "Writes one clear sentence for an image edit model, such as 'Replace the hat with a red cap.' It can add a line to keep the rest unchanged."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("instruction",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "action": (list(ACTIONS), {"default": "replace", "tooltip": "What kind of change you want."}),
                "target": ("STRING", {"default": "", "tooltip": "The part of the picture to change, for example 'red hat'."}),
                "keep_rest": ("BOOLEAN", {"default": True, "tooltip": "Adds a line asking the model to leave everything else alone."}),
            },
            "optional": {
                "to_value": ("STRING", {"default": "", "tooltip": "What it should become. Needed for every action except remove and fix_lighting."}),
                "extra": ("STRING", {"default": "", "tooltip": "Optional extra detail added after the main sentence."}),
            },
        }

    def run(self, action, target, keep_rest=True, to_value="", extra=""):
        return (build_edit_instruction(action, target, to_value, keep_rest, extra),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EditInstruction", SYEditInstruction)
