# Load Image From Folder SY (`SYLoadImageFromFolder`)

Source: `nodes/sy_load_image_from_folder.py`

**What it does:** Loads one picture from a folder inside the ComfyUI input folder. The index picks which one and wraps around.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| subfolder | STRING | yes | Folder inside the input folder. Empty means the input folder itself. | default '' |
| index | INT | yes | Which picture to load, from 0. Too big a number wraps to the start. | 0 to 2147483647, default 0 |
| sort_by | COMBO | yes | Order of the pictures: by file name, or by date (oldest first). | one of: name, date |

Outputs: `IMAGE`, `MASK`, `STRING`

## How it was tested

This node was not run by the harness. Reason: skipped: touches disk (the code reads or writes files).


## Verdict

Not run. skipped: touches disk (the code reads or writes files).
