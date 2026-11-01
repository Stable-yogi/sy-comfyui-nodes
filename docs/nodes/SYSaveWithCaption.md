# Save With Caption SY (`SYSaveWithCaption`)

Source: `nodes/sy_save_with_caption.py`

**What it does:** Saves each picture plus a text file with the same name holding the caption. Good for making training datasets. Can put a trigger word first (once), tidy tag captions (spaces, stray commas, repeated tags) and give one caption line per picture. Never overwrites: a taken name gets the next number.

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
| caption_mode | COMBO | no | same for all: one caption for every picture. one line per picture: line 1 for picture 1, and so on. | one of: same for all, one line per picture |
| trigger_word | STRING | no | A word put first in every caption, once, for example sks_style. Empty does nothing. | default '' |
| clean_tags | BOOLEAN | no | Tidy a comma caption: one line, no double spaces or stray commas, repeated tags removed. | default False |

Outputs: `STRING`, `STRING`, `STRING`

## How to use

1. Connect the pictures to images and type the caption.
2. Use caption_mode one line per picture to give each picture its own line, or same for all for one caption.
3. Optional: set trigger_word (put first, once) and turn on clean_tags to tidy a comma caption.
4. Set subfolder, filename_pattern and format. Each picture is saved with a .txt of the same name. Taken names get the next number.
