# Save Text SY (`SYSaveText`)

Source: `nodes/sy_save_text.py`

**What it does:** Saves text to a .txt file inside the ComfyUI output folder. Can add to the end of an existing file.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to save. | default '', multiline |
| subfolder | STRING | yes | Folder inside the output folder. It is created if missing. | default 'SY' |
| filename_pattern | STRING | yes | File name without .txt. Tokens: {date} {time} {seed} {counter}. | default 'text_{counter}' |
| append | BOOLEAN | yes | Add the text to the end of the file instead of making a new one. No {counter}. | default False |
| seed | INT | yes | Number used for the {seed} token. | 0 to 9007199254740992, default 0 |

Outputs: `STRING`
