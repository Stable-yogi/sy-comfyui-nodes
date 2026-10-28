# List Folder Files SY (`SYListFolderFiles`)

Source: `nodes/sy_list_folder_files.py`

**What it does:** Lists the files in a folder inside the input or output folder, one per line, with a count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| root | COMBO | yes | Which ComfyUI folder to look in. | one of: input, output |
| subfolder | STRING | yes | Folder inside it. Empty means the folder itself. | default '' |
| extensions | STRING | yes | File endings to keep, like png, jpg or txt. Empty lists every file. | default '' |

Outputs: `STRING`, `INT`

## How it was tested

This node was not run by the harness. Reason: skipped: needs the running app's folders (No module named 'folder_paths').


## Verdict

Not run. skipped: needs the running app's folders (No module named 'folder_paths').
