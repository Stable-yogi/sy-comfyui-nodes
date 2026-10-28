# Prompt Emphasis Strip SY (`SYPromptEmphasisStrip`)

Source: `nodes/sy_prompt_emphasis_strip.py`

**What it does:** Removes emphasis marks from a prompt: (word:1.2), ((word)) and [word] become word. Can also remove LoRA tags and BREAK.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt you want to clean. | default '', multiline |
| remove_lora_tags | BOOLEAN | yes | On: also remove tags like <lora:name:0.8>. | default False |
| remove_break | BOOLEAN | yes | On: also remove the word BREAK when it stands alone. | default False |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | remove_lora_tags = True | PASS | STRING=str '' |
| 4 | remove_break = True | PASS | STRING=str '' |

## Verdict

All 4 cases behaved as expected (4 passed, 0 rejected with a clear message).
