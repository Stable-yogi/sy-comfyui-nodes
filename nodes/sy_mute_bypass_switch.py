"""Mute/Bypass Switch SY: one small switch that turns chosen nodes on, muted or bypassed.
The switching happens in the browser (js/sy_mute_bypass_switch.js). This file holds the node shell and the plain rules
(the same rules are in js/sy_mute_bypass_switch_logic.js), so they can be tested without a browser."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODE_ON = 0
MODE_MUTE = 2
MODE_BYPASS = 4
OFF_MODES = ["mute", "bypass"]


def mode_number(on, off_mode):
    """The LiteGraph mode number: 0 runs, 2 is muted, 4 is bypassed. Anything but 'bypass' means mute."""
    if on:
        return MODE_ON
    return MODE_BYPASS if str(off_mode).strip().lower() == "bypass" else MODE_MUTE


def parse_ids(text):
    """Node ids from a saved list: a JSON list such as [3, "7"]. Whole numbers only, no duplicates, broken input gives []."""
    try:
        data = json.loads(text) if isinstance(text, str) else text
    except ValueError:
        return []
    out = []
    if not isinstance(data, list):
        return out
    for v in data:
        if isinstance(v, bool):
            continue
        if isinstance(v, int) and v >= 0:
            i = v
        elif isinstance(v, str) and v.strip().isdigit():
            i = int(v.strip())
        else:
            continue
        if i not in out:
            out.append(i)
    return out


def add_ids(current, new_ids, own_id=None):
    """The saved list plus new node ids. The switch itself is never added, duplicates are skipped."""
    out = parse_ids(current)
    for i in parse_ids(list(new_ids or [])):
        if i != own_id and i not in out:
            out.append(i)
    return out


def plan_pair(switches, changed_id):
    """switches: [{'id', 'pair', 'on'}]. When the changed switch is ON and has a pair name, every OTHER switch that is on
    with the same pair name (spaces and capitals ignored) must go OFF. Returns those ids in list order.
    Turning one off changes only itself."""
    me = next((s for s in (switches or []) if s.get("id") == changed_id), None)
    if me is None or not me.get("on"):
        return []
    name = str(me.get("pair") or "").strip().lower()
    if not name:
        return []
    return [s["id"] for s in switches
            if s.get("id") != changed_id and s.get("on") and str(s.get("pair") or "").strip().lower() == name]


class SYMuteBypassSwitch:
    DESCRIPTION = ("One switch for the nodes you choose. Select nodes on the canvas and press Add selected nodes. On runs them, "
                   "off mutes them (they stop) or bypasses them (the data passes through). Give two or more switches the same "
                   "pair name and only one of them can be on at a time. It has no wires itself.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ()
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "on": ("BOOLEAN", {"default": True, "label_on": "on", "label_off": "off", "tooltip": "On runs the chosen nodes. Off mutes or bypasses them."}),
                "off_mode": (OFF_MODES, {"default": "mute", "tooltip": "What off does. Mute stops the node. Bypass lets the data pass through it."}),
            },
            "optional": {
                "pair": ("STRING", {"default": "", "multiline": False, "tooltip": "Same pair name on several switches = radio buttons: one on turns the others off. Empty = free switch."}),
            },
        }

    def run(self, on=True, off_mode="mute", pair=""):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "MuteBypassSwitch", SYMuteBypassSwitch)
