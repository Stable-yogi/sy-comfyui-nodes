# Workflow Header SY (`SYWorkflowHeader`)

Source: `nodes/sy_workflow_header.py`

**What it does:** A title banner for the top of a workflow with a workflow number (Workflow 1, 2, 3), three help buttons (Nodes to Install, How to Use, Nodes Info) and three link buttons (GitHub, Website, YouTube). Fill the number, the title and the three texts with the Edit button in the browser. It has no inputs or outputs and does nothing when the workflow runs, so you can leave it in for people you share the workflow with.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| (none) | | | | |

Outputs: none

## How to use

1. Add the node to the top of a workflow. It has no inputs or outputs.
2. Use the Edit button in the browser to fill the workflow number, the title and the three help texts.
3. In the subtitle and the three help texts you can start a line with `#`, `##` or `###` for a header, `- ` for a list item, and use `**bold**`, `*italic*` and `` `code` ``. Anything else is shown as typed.
4. It does nothing when the workflow runs. Viewers use its help and link buttons.
