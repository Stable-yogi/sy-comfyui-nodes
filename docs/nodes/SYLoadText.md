# Load Text SY (`SYLoadText`)

Source: `nodes/sy_load_text.py`

**What it does:** Loads the text of a .txt file from the ComfyUI input folder. Other file types are refused. Optional line picks one line (1 = first), strip trims lines, skip_comments ignores lines starting with #, and if_missing can answer empty text for a file that is not there. Also gives the line count and an info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| file | STRING | yes | Path of a .txt file inside the input folder, like notes.txt or a/b.txt. | default 'notes.txt' |
| line | INT | no | 0 = the whole text. 1 = only the first line, 2 = the second, and so on. | 0 to 1000000, default 0 |
| strip | BOOLEAN | no | On: trim spaces around each line and empty lines at the start and end. | default False |
| skip_comments | BOOLEAN | no | On: ignore lines that start with #. | default False |
| if_missing | COMBO | no | error stops with a clear message. empty gives empty text. | one of: error, empty |

Outputs: `STRING`, `INT`, `STRING`
