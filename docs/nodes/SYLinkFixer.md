# LinkFixer SY (`SYLinkFixer`)

Source: `nodes/sy_link_fixer.py`

**What it does:** Finds broken wires in the open workflow and repairs them. Press Check wires to see the list, Repair broken wires to fix them. Wires that only join unlike kinds of data are listed but never changed. It has no wires itself.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| repair_on_open | BOOLEAN | yes | On repairs broken wires by itself each time this workflow is opened. | default False |

Outputs: none

## How to use

1. Add Link Fixer SY to the workflow you want to check.
2. Press Check wires. The list shows broken wires, such as a wire to a node that is gone. Nothing is changed.
3. Press Repair broken wires to remove them. Wires that join two different kinds of data are only reported, never changed.
4. To check a saved workflow file before ComfyUI opens it, press Repair a workflow file, pick the .json, then Open repaired copy. The file itself is never changed.
Turn repair_on_open on to repair once each time a workflow with this node is opened. Note: this ComfyUI version already heals most broken wires when it loads a workflow, so the file check is the most useful part.
