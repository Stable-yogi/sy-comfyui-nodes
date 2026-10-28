import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_workflow_header as m


def run():
    n = 0
    out = m.clean_panels(None)
    assert set(out) == {"sy_title", "sy_subtitle", "sy_install", "sy_howto", "sy_info"}; n += 1
    assert all(v == "" for v in out.values()); n += 1
    out = m.clean_panels({"sy_title": "Krea 2", "sy_howto": 5, "other": "x"})
    assert out["sy_title"] == "Krea 2" and out["sy_howto"] == "5" and "other" not in out; n += 1
    assert m.SYWorkflowHeader.RETURN_TYPES == (); n += 1
    assert m.SYWorkflowHeader.INPUT_TYPES() == {"required": {}}; n += 1
    assert m.SYWorkflowHeader().run() == (); n += 1
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYWorkflowHeader"] == "Workflow Header SY"; n += 1
    return n
