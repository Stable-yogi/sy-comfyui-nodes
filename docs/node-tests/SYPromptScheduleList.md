# Prompt Schedule List SY (`SYPromptScheduleList`)

Source: `nodes/sy_prompt_schedule_list.py`

**What it does:** Turns a prompt schedule into a list with one prompt per frame, one per line. Also tells how many segments it has.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | One line per key, written as frame: prompt. Blank lines and # lines are skipped. | default '0: a cat\n24: a dog', multiline |
| total_frames | INT | yes | How many frames to list. The most allowed is 2000. | 1 to 2000, default 48 |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat...'; INT=int 2 |
| 2 | text = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 3 | total_frames = 1 (min) | PASS | STRING=str 'a cat'; INT=int 1 |
| 4 | total_frames = 2000 (max) | PASS | STRING=str 'a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat...'; INT=int 2 |
| 5 | total_frames = 1000 (mid) | PASS | STRING=str 'a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat a cat...'; INT=int 2 |

## Verdict

All 5 cases behaved as expected (5 passed, 0 rejected with a clear message).
