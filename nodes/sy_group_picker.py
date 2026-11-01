"""Group Picker SY: pick ONE group of the workflow. Its nodes switch on, the nodes of the other listed groups switch off.
The choice is saved with the workflow and put back when the workflow opens. The switching itself happens in the browser
(js/sy_group_picker.js). This file holds the node shell and the plain rules, so they can be tested without a browser."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

OFF_MODES = ("bypass", "mute")


def parse_words(text):
    """Pure function. Splits a comma list into lower-case words. Empty pieces are dropped."""
    return [w.strip().lower() for w in str(text or "").split(",") if w.strip()]


def chosen_index(titles, choice):
    """Pure function. Index of the group called choice (same letters, any case, spaces at the ends ignored), or -1."""
    want = str(choice or "").strip().lower()
    if not want:
        return -1
    for i, t in enumerate(titles):
        if str(t).strip().lower() == want:
            return i
    return -1


def plan(titles, choice):
    """Pure function. One word per group: "on" for the chosen group, "off" for every other.
    Returns an empty list when no group has that name (nothing should change then)."""
    k = chosen_index(titles, choice)
    if k < 0:
        return []
    return ["on" if i == k else "off" for i in range(len(titles))]


def off_mode_for(title, off_mode, bypass_words):
    """Pure function. How a node is switched off. A node whose title holds one of the bypass words is bypassed
    (data passes through, so a switch further down can pick another source); every other node uses off_mode."""
    low = str(title or "").lower()
    if any(w and w in low for w in parse_words(bypass_words)):
        return "bypass"
    return "mute" if off_mode == "mute" else "bypass"


class SYGroupPicker:
    DESCRIPTION = ("Pick one group of the workflow. Its nodes switch on and the nodes of the other groups switch off (mute or bypass). "
                   "The choice is saved with the workflow and put back when you open it. Nodes outside the listed groups are never touched. "
                   "The output is the name of the chosen group.")
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("choice",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "choice": ("STRING", {"default": "", "tooltip": "The title of the chosen group. Set it by clicking in the list."}),
                "title_filter": ("STRING", {"default": "", "tooltip": "Only list groups whose title has this text. Empty lists all groups."}),
                "off_mode": (list(OFF_MODES), {"default": "mute", "tooltip": "Mute stops the node. Bypass passes data through."}),
                "bypass_words": ("STRING", {"default": "", "tooltip": "Comma list. A node with one of these words in its title is bypassed instead of muted. Example: image"}),
                "apply_on_open": ("BOOLEAN", {"default": True, "tooltip": "Put the choice back when the workflow opens."}),
            }
        }

    def run(self, choice="", title_filter="", off_mode="mute", bypass_words="", apply_on_open=True):
        return (str(choice or ""),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "GroupPicker", SYGroupPicker)
NODE_DISPLAY_NAME_MAPPINGS["SYGroupPicker"] = "Group Picker SY"
