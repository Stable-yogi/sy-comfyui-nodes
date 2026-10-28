# Save Image To Folder SY (`SYSaveImageToFolder`)

Source: `nodes/sy_save_image_to_folder.py`

**What it does:** Saves pictures into a folder inside the ComfyUI output folder. The name can use {date} {time} {seed} {counter}.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures to save. | picture batch [B,H,W,3] |
| subfolder | STRING | yes | Folder inside the output folder. It is created if missing. No .. or drive letters. | default 'SY' |
| filename_pattern | STRING | yes | File name without extension. Tokens: {date} {time} {seed} {counter}. | default 'image_{counter}' |
| format | COMBO | yes | File type to save. | one of: png, jpg, webp |
| quality | INT | yes | Quality for jpg and webp. Png ignores it. | 1 to 100, default 95 |
| seed | INT | yes | Number used for the {seed} token. | 0 to 9007199254740992, default 0 |
| embed_workflow | BOOLEAN | yes | Store the prompt and workflow inside png files so you can reload them. | default True |

Outputs: `STRING`

## How it was tested

This node was not run by the harness. Reason: skipped: needs the running app's folders (No module named 'folder_paths').


## Verdict

Not run. skipped: needs the running app's folders (No module named 'folder_paths').
