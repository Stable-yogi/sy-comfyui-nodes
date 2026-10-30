# ImageExists SY (`SYImageExists`)

Source: `nodes/sy_image_exists.py`

**What it does:** Tells you if a file is there. Looks only inside the input, output or temp folder.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| folder | COMBO | yes | Which ComfyUI folder to look in. | one of: input, output, temp |
| filename | STRING | yes | File name inside that folder, for example refs/hero.png. | default '' |

Outputs: `BOOLEAN`, `STRING`
