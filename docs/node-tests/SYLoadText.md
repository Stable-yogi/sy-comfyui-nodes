# Load Text SY (`SYLoadText`)

Source: `nodes/sy_load_text.py`

**What it does:** Loads the text of a .txt file from the ComfyUI input folder. Other file types are refused.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| file | STRING | yes | Path of a .txt file inside the input folder, like notes.txt or a/b.txt. | default 'notes.txt' |

Outputs: `STRING`

## How it was tested

This node was not run by the harness. Reason: skipped: touches disk (the code reads or writes files).


## Verdict

Not run. skipped: touches disk (the code reads or writes files).
