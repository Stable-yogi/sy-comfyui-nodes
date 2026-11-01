# Save Pack SY (`SYSavePack`)

Source: `nodes/sy_save_pack.py`

**What it does:** Saves pictures into the ComfyUI output folder. The file name is built from tokens {date} {time} {name} {seed} {steps} {cfg} {width} {height} {format} {counter} {batch}. Never overwrites. Optional settings text file beside every picture (also stored inside png files).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures to save. A batch saves every picture. | picture batch [B,H,W,3] |
| filename_pattern | STRING | no | File name without ending. Tokens: {date} {time} {name} {seed} {steps} {cfg} {width} {height} {format} {counter} {batch}. | default '{date}_{name}_{counter}' |
| name | STRING | no | Text for the {name} token. Bad file name characters are replaced. | default 'image' |
| subfolder | STRING | no | Folder inside the output folder, made if missing. May use tokens such as {date}. Empty: the output folder. | default '' |
| format | COMBO | no | File type. png keeps the workflow inside the file. | one of: png, jpeg, webp |
| quality | INT | no | Quality for jpeg and webp. png ignores it. | 1 to 100, default 95 |
| seed | INT | no | Number for the {seed} token. -1 means not used. | -1 to 9007199254740992, default 0 |
| steps | INT | no | Number for the {steps} token. 0 means not used. | 0 to 1000, default 0 |
| cfg | FLOAT | no | Number for the {cfg} token. 0 means not used. | 0.0 to 100.0, step 0.1, default 0.0 |
| settings_text | STRING | no | Extra text for the settings file, for example the prompt. | default '', multiline |
| write_settings_file | BOOLEAN | no | On: a .txt beside every picture with seed, steps, cfg, size, date and your text. | default True |
| on_exists | COMBO | no | When the exact name is taken: use the next number, or skip that picture. | one of: next number, skip |

Outputs: `STRING`, `STRING`
