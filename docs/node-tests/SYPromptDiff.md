# Prompt Diff SY (`SYPromptDiff`)

Source: `nodes/sy_prompt_diff.py`

**What it does:** Compares the tags of two prompts. Gives the tags only in A, only in B and shared by both, with counts.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text_a | STRING | yes | The first prompt. | default '', multiline |
| text_b | STRING | yes | The second prompt to compare with the first. | default '', multiline |
| separator | STRING | yes | The character that splits one tag from the next. | default ',' |

Outputs: `STRING`, `STRING`, `STRING`, `INT`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str ''; STRING=str ''; STRING=str ''; INT=int 0; INT=int 0; INT=int 0 |
| 2 | text_a = '' (empty) | PASS | STRING=str ''; STRING=str ''; STRING=str ''; INT=int 0; INT=int 0; INT=int 0 |
| 3 | text_b = '' (empty) | PASS | STRING=str ''; STRING=str ''; STRING=str ''; INT=int 0; INT=int 0; INT=int 0 |
| 4 | separator = '' (empty) | REJECTED | ValueError: separator is empty: type the character that splits the tags, for example a comma |

## Verdict

All 4 cases behaved as expected (3 passed, 1 rejected with a clear message).
