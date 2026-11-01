# Folder Image Count SY (`SYFolderImageCount`)

Source: `nodes/sy_folder_image_count.py`

**What it does:** Counts the picture files (png, jpg, jpeg, webp, bmp, gif, tif) in a folder inside the input or output folder. Optional extensions count other file types, include_subfolders looks deeper, and if_missing can stop with a clear message for a folder that is not there. Also gives the last valid index and an info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| root | COMBO | yes | Which ComfyUI folder to look in. | one of: input, output |
| subfolder | STRING | yes | Folder inside it. Empty means the folder itself. | default '' |
| extensions | STRING | no | Optional endings to count, like 'png, webp'. Empty counts all picture types. | default '' |
| include_subfolders | BOOLEAN | no | On: also count files in the folders below. | default False |
| if_missing | COMBO | no | empty answers 0 for a missing folder. error stops with a clear message. | one of: empty, error |

Outputs: `INT`, `INT`, `STRING`
