"""Group Switch SY: one panel with an on/off switch for every group in the workflow.
The switching itself happens in the browser (js/sy_group_switch.js). This file holds the node
shell and the plain rules the panel follows, so the rules can be tested without a browser."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

OFF_MODES = ("bypass", "mute")
SORTS = ("position", "alphabetical")


def visible_groups(titles, needle=""):
    """Pure function. Keeps the group titles that contain the filter text (any case). Empty filter keeps all.
    Returns the kept titles in their old order."""
    needle = str(needle or "").strip().lower()
    return [t for t in titles if needle in str(t).lower()]


def next_states(titles, states, clicked, turn_on, exclusive=False):
    """Pure function. titles and states are two lists of the same length (states are True for on).
    clicked is the index of the group the user pressed and turn_on is what it should become.
    With exclusive on, turning one group on turns every other group off. Turning one off changes only that one.
    Returns a new list of states."""
    if len(titles) != len(states):
        raise ValueError("titles and states must have the same length")
    if not 0 <= clicked < len(states):
        raise ValueError("clicked group %d does not exist (there are %d groups)" % (clicked, len(states)))
    out = [bool(s) for s in states]
    if turn_on and exclusive:
        out = [False] * len(out)
    out[clicked] = bool(turn_on)
    return out


class SYGroupSwitch:
    DESCRIPTION = ("Shows every group of the workflow with an on/off switch. Off turns all nodes in that group off (bypass or mute). "
                   "Use it to switch whole parts of a workflow, like an upscale part, with one click. It runs nothing itself.")
    CATEGORY = category("Logic")
    FUNCTION = "run"
    RETURN_TYPES = ()
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "title_filter": ("STRING", {"default": "", "tooltip": "Only list groups whose title has this text. Empty lists all groups."}),
                "off_mode": (list(OFF_MODES), {"default": "bypass", "tooltip": "Bypass passes data through. Mute stops the node."}),
                "sort": (list(SORTS), {"default": "position", "tooltip": "Order of the list: top to bottom on the canvas, or by title."}),
                "one_at_a_time": ("BOOLEAN", {"default": False, "tooltip": "When on, switching one group on switches all others off."}),
            }
        }

    def run(self, title_filter="", off_mode="bypass", sort="position", one_at_a_time=False):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "GroupSwitch", SYGroupSwitch)
