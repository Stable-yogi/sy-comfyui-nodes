"""Character Sheet Prompt SY: writes a prompt for a character reference sheet with the views you choose."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

BACKGROUNDS = ("plain_white", "plain_grey", "transparent_look", "none")
LAYOUTS = ("grid", "row")
_BG_TEXT = {
    "plain_white": "Use a plain white background.",
    "plain_grey": "Use a plain grey background.",
    "transparent_look": "Use a clean, empty background that looks transparent, with no scenery.",
    "none": "",
}
_VIEW_TEXT = (
    ("front", "front view"),
    ("side", "side view"),
    ("back", "back view"),
    ("three_quarter", "three-quarter view"),
    ("face_close_up", "face close-up"),
    ("full_body", "full-body shot"),
)


POSES = ("any", "neutral standing", "A-pose", "T-pose")
_POSE_TEXT = {
    "any": "",
    "neutral standing": "Every figure stands relaxed in a neutral pose.",
    "A-pose": "Every figure stands in an A-pose, arms slightly away from the body.",
    "T-pose": "Every figure stands in a T-pose, arms straight out to the sides.",
}


def _join(items):
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def sheet_info(views, background, layout, pose="any"):
    """Pure function. One plain line: how many views, which, and what canvas shape fits."""
    chosen = [text for key, text in _VIEW_TEXT if views.get(key)]
    n = len(chosen)
    if n == 0:
        return "No view is chosen."
    if layout == "row":
        shape = "a wide canvas, about %d:1" % n if n > 1 else "a normal canvas"
    else:
        shape = "a roughly square canvas" if n > 1 else "a normal canvas"
    extra = "" if pose == "any" else ", pose %s" % pose
    return "%d view%s (%s), %s, background %s%s. Try %s." % (n, "" if n == 1 else "s", ", ".join(chosen), layout, background, extra, shape)


def build_character_sheet(character, views, background, layout, pose="any", style_notes=""):
    """Pure function. views is a dict like {"front": True}. Returns the prompt text."""
    c = " ".join(str(character or "").split())
    if not c:
        raise ValueError("character is empty: describe the person or creature")
    if background not in BACKGROUNDS:
        raise ValueError("unknown background %r: choose one of %s" % (background, ", ".join(BACKGROUNDS)))
    if layout not in LAYOUTS:
        raise ValueError("unknown layout %r: choose one of %s" % (layout, ", ".join(LAYOUTS)))
    chosen = [text for key, text in _VIEW_TEXT if views.get(key)]
    if not chosen:
        raise ValueError("no view is chosen: turn on at least one view")
    arrange = "in a neat grid" if layout == "grid" else "side by side in one row"
    parts = [
        "A character reference sheet of %s." % c.rstrip("."),
        "Show %s, arranged %s." % (_join(chosen), arrange),
        "Keep the same face, the same hair and the same outfit in every view.",
    ]
    if _BG_TEXT[background]:
        parts.append(_BG_TEXT[background])
    if pose not in POSES:
        raise ValueError("unknown pose %r: choose one of %s" % (pose, ", ".join(POSES)))
    if _POSE_TEXT[pose]:
        parts.append(_POSE_TEXT[pose])
    notes = " ".join(str(style_notes or "").split())
    if notes:
        parts.append(notes if notes.endswith((".", "!", "?")) else notes + ".")
    return " ".join(parts)


def _flag(default, tip):
    return ("BOOLEAN", {"default": default, "tooltip": tip})


class SYCharacterSheetPrompt:
    DESCRIPTION = ("Writes a prompt that asks for a character reference sheet with the views you pick, with the same face and outfit in each view. "
                   "Can also ask for a pose and add style notes, and an info line suggests a canvas shape.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "character": ("STRING", {"default": "", "multiline": True, "tooltip": "Describe the character: looks, clothes, age, anything that must stay the same."}),
                "front": _flag(True, "Include a front view."),
                "side": _flag(True, "Include a side view."),
                "back": _flag(True, "Include a back view."),
                "three_quarter": _flag(False, "Include a three-quarter view."),
                "face_close_up": _flag(False, "Include a close-up of the face."),
                "full_body": _flag(False, "Include a full-body shot."),
                "background": (list(BACKGROUNDS), {"default": "plain_white", "tooltip": "The background behind the character."}),
                "layout": (list(LAYOUTS), {"default": "grid", "tooltip": "Put the views in a grid or in one row."}),
            },
            "optional": {
                "pose": (list(POSES), {"default": "any", "tooltip": "Ask for one pose in every view. A-pose or T-pose help later 3D work."}),
                "style_notes": ("STRING", {"default": "", "multiline": True, "tooltip": "Extra wishes, for example: flat colours, clean line art."}),
            },
        }

    def run(self, character, front, side, back, three_quarter, face_close_up, full_body, background, layout, pose="any", style_notes=""):
        views = {"front": front, "side": side, "back": back, "three_quarter": three_quarter,
                 "face_close_up": face_close_up, "full_body": full_body}
        return (build_character_sheet(character, views, background, layout, pose, style_notes),
                sheet_info(views, background, layout, pose))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CharacterSheetPrompt", SYCharacterSheetPrompt)
