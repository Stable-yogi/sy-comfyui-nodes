# Save With Caption SY (`SYSaveWithCaption`)

Source: `nodes/sy_save_with_caption.py`

**What it does:** Saves each picture plus a text file with the same name holding the caption. Good for making training datasets.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures to save. | picture batch [B,H,W,3] |
| caption | STRING | yes | Text written to the .txt file next to each picture. | default '', multiline |
| subfolder | STRING | yes | Folder inside the output folder. It is created if missing. | default 'SY/dataset' |
| filename_pattern | STRING | yes | File name without extension. Tokens: {date} {time} {seed} {counter}. | default 'img_{counter}' |
| format | COMBO | yes | Picture file type. | one of: png, jpg, webp |
| quality | INT | yes | Quality for jpg and webp. Png ignores it. | 1 to 100, default 95 |
| seed | INT | yes | Number used for the {seed} token. | 0 to 9007199254740992, default 0 |

Outputs: `STRING`
