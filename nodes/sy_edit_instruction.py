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


def _drop_article(text):
    """Remove a leading the/a/an so 'Replace the the hat' cannot happen."""
    words = text.split(" ", 1)
    if len(words) == 2 and words[0].lower() in ("the", "a", "an"):
        return words[1].strip()
    return text


def build_edit_instruction(action, target, to_value="", keep_rest=True, extra="", keep_detail=""):
    """Pure function. Returns the instruction text."""
    if action not in ACTIONS:
        raise ValueError("unknown action %r: choose one of %s" % (action, ", ".join(ACTIONS)))
    t = _drop_article(_clean(target))
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
    k = _clean(keep_detail)
    if k:
        text += " Keep %s exactly the same." % k
    if keep_rest:
        text += " " + KEEP_SENTENCE
    return text


def instruction_notes(action, target, to_value="", text=""):
    """Pure function. Plain warnings about the input, or 'OK: no warnings.'"""
    notes = []
    if action not in NEEDS_VALUE and _clean(to_value):
        notes.append("to_value was ignored: '%s' does not need it." % action)
    first = _clean(target).split(" ", 1)
    if len(first) == 2 and first[0].lower() in ("the", "a", "an"):
        notes.append("The word '%s' at the start of target was dropped." % first[0])
    count = len(text.split())
    if count > 60:
        notes.append("The instruction is %d words long; most edit models do better with a short one." % count)
    return " ".join(notes) if notes else "OK: no warnings."


class SYEditInstruction:
    DESCRIPTION = ("Writes one clear sentence for an image edit model, such as 'Replace the hat with a red cap.' It can add a line to keep "
                   "the rest unchanged, or to keep one named thing (for example the face). A notes line warns about ignored or too long input.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("instruction", "notes")

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
                "keep_detail": ("STRING", {"default": "", "tooltip": "Name what must not change, for example: the face and the pose."}),
            },
        }

    def run(self, action, target, keep_rest=True, to_value="", extra="", keep_detail=""):
        text = build_edit_instruction(action, target, to_value, keep_rest, extra, keep_detail)
        return (text, instruction_notes(action, target, to_value, text))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EditInstruction", SYEditInstruction)
