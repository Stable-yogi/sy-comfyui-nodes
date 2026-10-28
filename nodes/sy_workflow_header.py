"""Workflow Header SY: a big title banner with three help buttons for the top of a workflow.

The texts live in the node properties (set in the browser panel). The node does nothing when a workflow runs.
"""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

PANELS = ("sy_install", "sy_howto", "sy_info")
PANEL_BUTTONS = {"sy_install": "Nodes to Install", "sy_howto": "How to Use", "sy_info": "Nodes Info"}


def clean_panels(props):
    """Pure function. Keeps only the known keys of a properties dict and turns every value into text."""
    props = props or {}
    out = {"sy_title": str(props.get("sy_title", "")), "sy_subtitle": str(props.get("sy_subtitle", ""))}
    for key in PANELS:
        out[key] = str(props.get(key, ""))
    return out


class SYWorkflowHeader:
    DESCRIPTION = "A title banner for the top of a workflow with three buttons: Nodes to Install, How to Use and Nodes Info. It does nothing when the workflow runs."
    CATEGORY = category("Notes")
    FUNCTION = "run"
    RETURN_TYPES = ()

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    def run(self):
        return ()


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "WorkflowHeader", SYWorkflowHeader)
NODE_DISPLAY_NAME_MAPPINGS["SYWorkflowHeader"] = "Workflow Header SY"
