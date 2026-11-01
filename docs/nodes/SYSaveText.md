# Save Text SY (`SYSaveText`)

Source: `nodes/sy_save_text.py`

**What it does:** Saves text to a file inside the ComfyUI output folder and never overwrites: a taken name gets the next number. Can add to the end of one file for a running log (with a time stamp per entry), pick txt, md, csv, json or log, and skip empty texts. Gives the saved path and a plain info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to save. | default '', multiline |
| subfolder | STRING | yes | Folder inside the output folder. It is created if missing. | default 'SY' |
| filename_pattern | STRING | yes | File name without the extension. Tokens: {date} {time} {seed} {counter}. | default 'text_{counter}' |
| append | BOOLEAN | yes | Add the text to the end of the file instead of making a new one. No {counter}. | default False |
| seed | INT | yes | Number used for the {seed} token. | 0 to 9007199254740992, default 0 |
| extension | COMBO | no | File type to write. The text is saved as it is, nothing is converted. | one of: txt, md, csv, json, log |
| on_empty | COMBO | no | When the text is empty: save an empty file, skip saving, or stop with a message. | one of: save anyway, skip, error |
| time_stamp | BOOLEAN | no | Put [date time] in front of the text. Handy with append for a running log. | default False |

Outputs: `STRING`, `STRING`

## How to use

1. Connect the text to text and set subfolder, filename_pattern and extension.
2. Turn on append to add to the end of one file. Add time_stamp for a dated running log.
3. Set on_empty to choose what happens with empty text: save anyway, skip or stop with a message.
4. A taken name gets the next number. The saved path and an info line come out.
