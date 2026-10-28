# Prompt Schedule SY (`SYPromptSchedule`)

Source: `nodes/sy_prompt_schedule.py`

**What it does:** Reads lines like '0: a cat' and '24: a dog' and gives the prompt that is active at the frame you choose.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | One line per key, written as frame: prompt. Blank lines and # lines are skipped. | default '0: a cat\n24: a dog', multiline |
| frame | INT | yes | The frame to look up. | 0 to 10000000, default 0 |

Outputs: `STRING`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'a cat'; INT=int 24; INT=int 2 |
| 2 | text = '' (empty) | PASS | STRING=str ''; INT=int -1; INT=int 0 |
| 3 | frame = 10000000 (max) | PASS | STRING=str 'a dog'; INT=int -1; INT=int 2 |
| 4 | frame = 5000000 (mid) | PASS | STRING=str 'a dog'; INT=int -1; INT=int 2 |

## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).
