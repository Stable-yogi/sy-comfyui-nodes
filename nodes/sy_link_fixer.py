"""Link Fixer SY: finds broken wires in a workflow and repairs them.
The check and the repair run in the browser (js/sy_link_fixer.js) on the open workflow. This file holds the node shell and the plain rules
(the same rules are in js/sy_link_fixer_logic.js), so they can be tested on a saved workflow."""
import copy

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

TEXT = {
    "node_missing": "A wire points to a node that is not there",
    "slot_range": "A wire points to a socket the node does not have",
    "orphan": "A wire that its target socket does not know about",
    "input_dangling": "A socket remembers a wire that does not exist",
    "input_wrong_link": "A socket remembers a wire that goes somewhere else",
    "output_dangling": "An output remembers a wire that does not exist",
    "output_wrong_link": "An output remembers a wire that starts somewhere else",
    "type_mismatch": "The two ends carry different kinds of data (only reported, never changed)",
}


def norm_links(links):
    """Pure function. Wires from a saved workflow (list form [id, from_node, from_slot, to_node, to_slot, type] or dict form)
    as a dict id -> dict. Entries that are neither are skipped."""
    out = {}
    if isinstance(links, dict):
        links = list(links.values())
    for l in links or []:
        if isinstance(l, (list, tuple)) and len(l) >= 5:
            d = {"id": l[0], "origin_id": l[1], "origin_slot": l[2], "target_id": l[3], "target_slot": l[4], "type": l[5] if len(l) > 5 else None}
        elif isinstance(l, dict) and all(k in l for k in ("id", "origin_id", "origin_slot", "target_id", "target_slot")):
            d = {k: l.get(k) for k in ("id", "origin_id", "origin_slot", "target_id", "target_slot", "type")}
        else:
            continue
        if isinstance(d["id"], bool) or not isinstance(d["id"], int):
            continue
        out[d["id"]] = d
    return out


def types_clash(a, b):
    """Pure function. True only when both ends name a kind of data and the kinds share nothing. '*' and empty fit everything."""
    a = {t.strip().upper() for t in str(a or "").split(",") if t.strip()}
    b = {t.strip().upper() for t in str(b or "").split(",") if t.strip()}
    if not a or not b or "*" in a or "*" in b:
        return False
    return not (a & b)


def find_problems(wf):
    """Pure function. wf is a saved workflow dict with 'nodes' and 'links'. Returns a list of
    {'kind', 'link', 'node', 'slot', 'text', 'fix'}; fix is None for a problem that is only reported."""
    nodes = {n.get("id"): n for n in (wf or {}).get("nodes", []) if isinstance(n, dict)}
    links = norm_links((wf or {}).get("links"))
    out = []
    seen_fix = set()

    def add(kind, link=None, node=None, slot=None, fix=None):
        key = None if fix is None else tuple(sorted(fix.items()))
        if key is not None:
            if key in seen_fix:
                return
            seen_fix.add(key)
        out.append({"kind": kind, "link": link, "node": node, "slot": slot, "text": TEXT[kind], "fix": fix})

    for lid in sorted(links):
        L = links[lid]
        o, t = nodes.get(L["origin_id"]), nodes.get(L["target_id"])
        fix = {"op": "removeLink", "id": lid}
        if o is None or t is None:
            add("node_missing", lid, fix=fix)
            continue
        outs, ins = o.get("outputs") or [], t.get("inputs") or []
        os_, ts = L["origin_slot"], L["target_slot"]
        if not (isinstance(os_, int) and 0 <= os_ < len(outs)) or not (isinstance(ts, int) and 0 <= ts < len(ins)):
            add("slot_range", lid, fix=fix)
            continue
        if ins[ts].get("link") != lid:
            add("orphan", lid, node=t.get("id"), slot=ts, fix=fix)
            continue
        if types_clash(outs[os_].get("type"), ins[ts].get("type")):
            add("type_mismatch", lid, node=t.get("id"), slot=ts)
    for nid in sorted(nodes, key=lambda x: (str(type(x)), x)):
        n = nodes[nid]
        for si, inp in enumerate(n.get("inputs") or []):
            lk = inp.get("link")
            if lk is None:
                continue
            L = links.get(lk)
            if L is None:
                add("input_dangling", node=nid, slot=si, fix={"op": "clearInput", "node": nid, "slot": si})
            elif L["target_id"] != nid or L["target_slot"] != si:
                add("input_wrong_link", lk, node=nid, slot=si, fix={"op": "clearInput", "node": nid, "slot": si})
        for si, outp in enumerate(n.get("outputs") or []):
            for lk in outp.get("links") or []:
                L = links.get(lk)
                if L is None:
                    add("output_dangling", lk, node=nid, slot=si, fix={"op": "dropOutputLink", "node": nid, "slot": si, "id": lk})
                elif L["origin_id"] != nid or L["origin_slot"] != si:
                    add("output_wrong_link", lk, node=nid, slot=si, fix={"op": "dropOutputLink", "node": nid, "slot": si, "id": lk})
    return out


def apply_fixes(wf, problems=None):
    """Pure function. Returns a repaired COPY of the workflow dict (the original is never changed) and the number of fixes made.
    removeLink also scrubs every socket that still names the wire, and never touches a socket that holds a different wire."""
    data = copy.deepcopy(wf)
    problems = find_problems(data) if problems is None else problems
    nodes = {n.get("id"): n for n in data.get("nodes", []) if isinstance(n, dict)}
    done = 0
    for p in problems:
        f = p.get("fix")
        if not f:
            continue
        if f["op"] == "removeLink":
            lid = f["id"]
            ls = data.get("links")
            if isinstance(ls, dict):
                ls.pop(lid, None)
                ls.pop(str(lid), None)
            elif isinstance(ls, list):
                data["links"] = [l for l in ls if not ((isinstance(l, (list, tuple)) and l and l[0] == lid) or (isinstance(l, dict) and l.get("id") == lid))]
            for n in nodes.values():
                for inp in n.get("inputs") or []:
                    if inp.get("link") == lid:
                        inp["link"] = None
                for outp in n.get("outputs") or []:
                    if outp.get("links"):
                        outp["links"] = [x for x in outp["links"] if x != lid]
        elif f["op"] == "clearInput":
            n = nodes.get(f["node"])
            ins = (n or {}).get("inputs") or []
            if n is not None and 0 <= f["slot"] < len(ins):
                ins[f["slot"]]["link"] = None
        elif f["op"] == "dropOutputLink":
            n = nodes.get(f["node"])
            outs = (n or {}).get("outputs") or []
            if n is not None and 0 <= f["slot"] < len(outs) and outs[f["slot"]].get("links"):
                outs[f["slot"]]["links"] = [x for x in outs[f["slot"]]["links"] if x != f["id"]]
        else:
            continue
        done += 1
    return data, done


class SYLinkFixer:
    DESCRIPTION = ("Finds broken wires in the open workflow and repairs them. Press Check wires to see the list, Repair broken wires to fix them. "
                   "Wires that only join unlike kinds of data are listed but never changed. It has no wires itself.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ()
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "repair_on_open": ("BOOLEAN", {"default": False, "tooltip": "On repairs broken wires by itself each time this workflow is opened."}),
            }
        }

    def run(self, repair_on_open=False):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LinkFixer", SYLinkFixer)
