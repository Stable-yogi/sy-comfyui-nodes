# Folder Image Count SY (`SYFolderImageCount`)

Source: `nodes/sy_folder_image_count.py`

**What it does:** Counts the picture files (png, jpg, jpeg, webp, bmp, gif, tif) in a folder inside the input or output folder.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| root | COMBO | yes | Which ComfyUI folder to look in. | one of: input, output |
| subfolder | STRING | yes | Folder inside it. Empty means the folder itself. | default '' |

Outputs: `INT`
