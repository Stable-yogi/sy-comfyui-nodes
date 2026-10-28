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

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '[removed]' |
| 2 | text = '' (empty) | PASS | STRING=str '[removed]' |
| 3 | subfolder = '' (empty) | PASS | STRING=str '[removed]' |
| 4 | filename_pattern = '' (empty) | REJECTED | ValueError: file name pattern is empty: type a name such as image_{counter} |
| 5 | append = True | REJECTED | ValueError: append needs a fixed file name: remove {counter} from the pattern |
| 6 | seed = 9007199254740992 (max) | PASS | STRING=str '[removed]' |
| 7 | seed = 4503599627370496 (mid) | PASS | STRING=str '[removed]' |

Note: this node refuses on purpose here (refuses append when the name pattern still has {counter}, with a clear message), so a plain-words refusal in any case is counted as REJECTED.


## Verdict

All 7 cases behaved as expected (5 passed, 2 rejected with a clear message).
