# ImageExists SY (`SYImageExists`)

Source: `nodes/sy_image_exists.py`

**What it does:** Tells you if a file is there. Looks only inside the input, output or temp folder. Optional ignore_case and try_extensions find a file when the capital letters or the ending do not match. Also gives the real file name found and an info line with the size, or close names when it is missing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| folder | COMBO | yes | Which ComfyUI folder to look in. | one of: input, output, temp |
| filename | STRING | yes | File name inside that folder, for example refs/hero.png. | default '' |
| ignore_case | BOOLEAN | no | On: Hero.PNG matches hero.png. | default False |
| try_extensions | BOOLEAN | no | On: also try picture endings (png, jpg, webp ...) when the name has none. | default False |

Outputs: `BOOLEAN`, `STRING`, `STRING`, `STRING`

## How to use

1. Pick folder (input, output or temp) and type filename inside it, for example refs/hero.png.
2. Turn on ignore_case to match different capitals, and try_extensions to also try picture endings when the name has none.
3. It looks only inside that folder. You get true or false, the real file name found, and an info line with the size, or close names when the file is missing.
