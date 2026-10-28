# Prompt Cleaner SY (`SYPromptCleaner`)

Source: `nodes/sy_prompt_cleaner.py`

**What it does:** Cleans a comma separated prompt: removes repeated tags, double commas and extra spaces. The order stays the same.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt to clean. Tags are split at commas. | default '', multiline |
| case_insensitive | BOOLEAN | yes | On: 'Cat' and 'cat' count as the same tag. The first one stays. | default True |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | case_insensitive = False | PASS | STRING=str '' |

## Verdict

All 3 cases behaved as expected (3 passed, 0 rejected with a clear message).
