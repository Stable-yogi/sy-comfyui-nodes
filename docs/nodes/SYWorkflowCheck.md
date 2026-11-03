# Workflow Check SY (`SYWorkflowCheck`)

Source: `nodes/sy_workflow_check.py`

**What it does:** Paste a workflow before you load it. Lists the node types and model files that are missing on this PC. It never loads or runs anything.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| workflow_json | STRING | yes | The text of a workflow saved from ComfyUI (normal or API format). | default '', multiline |
| workflow_file | STRING | no | A file name in the input folder. Used only when the text box is empty. | default '' |

Outputs: `STRING`, `STRING`, `STRING`, `INT`

## How to use

1. Open the shared workflow file in a text editor and copy all of its text.
2. Paste it into **workflow_json**. Or save the file into the ComfyUI input folder and type its name in **workflow_file**.
3. Run the node. The **report** starts with how many nodes were read and how many node types and model files are missing.
4. **missing_nodes** lists the node types you need to install a pack for, or replace. **missing_models** lists the model files to download.
5. **problem_count** is 0 when everything is there, so you can use it to stop a chain.

Model names that are only typed inside a text prompt are not checked. Notes, reroutes and subgraphs are never reported as missing.
