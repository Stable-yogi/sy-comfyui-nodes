# Load Text SY (`SYLoadText`)

Source: `nodes/sy_load_text.py`

**What it does:** Loads the text of a .txt file from the ComfyUI input folder. Other file types are refused.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| file | STRING | yes | Path of a .txt file inside the input folder, like notes.txt or a/b.txt. | default 'notes.txt' |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'first line second line' |
| 2 | file = '' (empty) | REJECTED | ValueError: file is empty: type the name of a .txt file in the input folder |

## Verdict

All 2 cases behaved as expected (1 passed, 1 rejected with a clear message).
