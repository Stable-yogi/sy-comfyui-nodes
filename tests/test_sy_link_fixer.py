import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_link_fixer as m


def good():
    """Node 1 (outputs IMAGE) -> node 2 (input IMAGE), link 5. Node 3 has a MODEL input fed by node 1's second output, link 6."""
    return {
        "nodes": [
            {"id": 1, "inputs": [], "outputs": [{"name": "img", "type": "IMAGE", "links": [5]}, {"name": "mdl", "type": "MODEL", "links": [6]}]},
            {"id": 2, "inputs": [{"name": "image", "type": "IMAGE", "link": 5}], "outputs": []},
            {"id": 3, "inputs": [{"name": "model", "type": "MODEL", "link": 6}], "outputs": []},
        ],
        "links": [[5, 1, 0, 2, 0, "IMAGE"], [6, 1, 1, 3, 0, "MODEL"]],
    }


def kinds(wf):
    return sorted(p["kind"] for p in m.find_problems(wf))


def run():
    n = 0
    assert m.find_problems(good()) == []; n += 1
    assert m.find_problems({}) == [] and m.find_problems(None) == [] and m.find_problems({"nodes": [], "links": []}) == []; n += 1
    # dict-form wires give the same answer as list-form
    d = good()
    d["links"] = [{"id": 5, "origin_id": 1, "origin_slot": 0, "target_id": 2, "target_slot": 0, "type": "IMAGE"},
                  {"id": 6, "origin_id": 1, "origin_slot": 1, "target_id": 3, "target_slot": 0, "type": "MODEL"}]
    assert m.find_problems(d) == []; n += 1
    # 1 wire whose node is gone
    w = good(); w["nodes"].pop(2)
    assert kinds(w) == ["node_missing"] or "node_missing" in kinds(w); n += 1
    r, done = m.apply_fixes(w)
    assert m.find_problems(r) == [] and done >= 1 and all(6 not in (o.get("links") or []) for nd in r["nodes"] for o in nd["outputs"]); n += 1
    # 2 slot out of range
    w = good(); w["links"][0][4] = 3
    assert "slot_range" in kinds(w); n += 1
    r, _ = m.apply_fixes(w)
    assert m.find_problems(r) == []; n += 1
    # 3 the input points to a wire that is not in the table
    w = good(); w["nodes"][1]["inputs"][0]["link"] = 999
    ks = kinds(w)
    assert "input_dangling" in ks and "orphan" in ks; n += 1
    r, _ = m.apply_fixes(w)
    assert m.find_problems(r) == [] and r["nodes"][1]["inputs"][0]["link"] is None; n += 1
    # 4 the output names a wire that is not there
    w = good(); w["nodes"][0]["outputs"][0]["links"].append(77)
    assert kinds(w) == ["output_dangling"]; n += 1
    r, done = m.apply_fixes(w)
    assert m.find_problems(r) == [] and r["nodes"][0]["outputs"][0]["links"] == [5] and done == 1; n += 1
    # 5 orphan: wire exists but the target socket is empty
    w = good(); w["nodes"][2]["inputs"][0]["link"] = None
    assert kinds(w) == ["orphan"]; n += 1
    r, _ = m.apply_fixes(w)
    assert m.find_problems(r) == [] and [l[0] for l in r["links"]] == [5]; n += 1
    # 6 orphan whose target socket holds a DIFFERENT valid wire: that other wire must survive
    w = good()
    w["nodes"].append({"id": 4, "inputs": [], "outputs": [{"name": "img2", "type": "IMAGE", "links": [8]}]})
    w["links"].append([8, 4, 0, 2, 0, "IMAGE"])      # a second wire into node 2 socket 0
    w["nodes"][1]["inputs"][0]["link"] = 8             # the socket knows wire 8, not wire 5
    assert kinds(w) == ["orphan"]; n += 1
    r, _ = m.apply_fixes(w)
    assert m.find_problems(r) == [] and r["nodes"][1]["inputs"][0]["link"] == 8 and [l[0] for l in r["links"]] == [6, 8]; n += 1
    # 7 socket names a wire that goes elsewhere
    w = good(); w["nodes"][2]["inputs"][0]["link"] = 5
    assert "input_wrong_link" in kinds(w); n += 1
    # 8 output names a wire that starts elsewhere
    w = good(); w["nodes"][1]["outputs"] = [{"name": "o", "type": "IMAGE", "links": [6]}]
    assert "output_wrong_link" in kinds(w); n += 1
    # 9 type mismatch is reported but never fixed
    w = good(); w["nodes"][1]["inputs"][0]["type"] = "MASK"
    ps = m.find_problems(w)
    assert [p["kind"] for p in ps] == ["type_mismatch"] and ps[0]["fix"] is None; n += 1
    r, done = m.apply_fixes(w)
    assert done == 0 and r == w; n += 1
    assert not m.types_clash("*", "IMAGE") and not m.types_clash("", "IMAGE") and not m.types_clash("IMAGE,MASK", "mask") and m.types_clash("IMAGE", "MASK"); n += 1
    # the original is never changed
    w = good(); w["nodes"][0]["outputs"][0]["links"].append(77)
    before = copy.deepcopy(w)
    m.apply_fixes(w)
    assert w == before; n += 1
    # several problems at once, one pass fixes everything but the mismatch
    w = good(); w["nodes"][0]["outputs"][0]["links"].append(77); w["nodes"][2]["inputs"][0]["link"] = None; w["links"].append([9, 42, 0, 1, 0, "IMAGE"])
    r, _ = m.apply_fixes(w)
    assert m.find_problems(r) == []; n += 1
    # damaged entries are skipped, not thrown
    w = good(); w["links"] += [None, 5, "x", [1, 2], {"id": "a"}]
    assert m.find_problems(w) == []; n += 1
    # shell
    cls = m.SYLinkFixer
    assert cls.RETURN_TYPES == () and cls().run() == () and "tooltip" in cls.INPUT_TYPES()["required"]["repair_on_open"][1]; n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYLinkFixer"] == "LinkFixer SY" and cls.DESCRIPTION; n += 1
    return n
