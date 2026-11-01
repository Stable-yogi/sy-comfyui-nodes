"""Stacking Keeper SY: keeps the front-to-back stacking of the nodes of a workflow.
ComfyUI forgets which node lies on top of which when a workflow is closed and opened again (nodes that were raised, such as
Set/Get nodes, fall back to the order of their numbers). This node writes the stacking into the saved workflow and puts it back
when the workflow opens. The work happens in the browser (js/sy_stacking_keeper.js). This file holds the node shell and the plain
rules, so they can be tested without a browser. The node has no wires and never runs."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MAX_IDS = 20000


def parse_order(text):
    """Pure function. Reads a saved stacking: a JSON list of node ids, back to front. Every id is kept as text
    (the page may hand out 12 or "12"). Anything else (bad JSON, other types, empty text, repeated ids) is dropped. Never raises."""
    import json

    try:
        data = json.loads(text) if isinstance(text, str) else text
    except (TypeError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    seen = set()
    out = []
    for v in data[:MAX_IDS]:
        if isinstance(v, bool) or not isinstance(v, (int, str)):
            continue
        key = str(v).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _sort_key(i):
    return (0, int(i), "") if i.isdigit() else (1, 0, i)


def merge_order(saved, ids):
    """Pure function. The stacking to apply now, back to front. Saved numbers that still exist keep their place;
    nodes that were added after the save (not in saved) are put on top, in number order, like a new node."""
    present = [str(i) for i in ids]
    have = set(present)
    kept = [i for i in saved if i in have]
    known = set(kept)
    return kept + sorted((i for i in have if i not in known), key=_sort_key)


def raise_to_front(order, node_id):
    """Pure function. Moves one node to the front (the end of the list). A node not in the list is added."""
    node_id = str(node_id)
    return [i for i in order if i != node_id] + [node_id]


def send_to_back(order, node_id):
    """Pure function. Moves one node to the back (the start of the list). A node not in the list is added."""
    node_id = str(node_id)
    return [node_id] + [i for i in order if i != node_id]


class SYStackingKeeper:
    DESCRIPTION = ("Keeps the front-to-back stacking of your nodes. ComfyUI forgets it when a workflow is closed and opened again, "
                   "so nodes you raised (Set and Get nodes for example) fall back behind others. Put one of these nodes anywhere "
                   "in the workflow: it saves the stacking with the workflow and puts it back when you open it. It has no wires and never runs.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "order": ("STRING", {"default": "[]", "tooltip": "The saved stacking, back to front. Filled in by the node."}),
                "restore_on_open": ("BOOLEAN", {"default": True, "tooltip": "Put the saved stacking back when the workflow opens."}),
            }
        }

    def run(self, order="[]", restore_on_open=True):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "StackingKeeper", SYStackingKeeper)
NODE_DISPLAY_NAME_MAPPINGS["SYStackingKeeper"] = "Stacking Keeper SY"
