# Caption Prefix Suffix SY (`SYCaptionPrefixSuffix`)

Source: `nodes/sy_caption_prefix_suffix.py`

**What it does:** Adds a trigger word before and/or after a caption. Skips it when the caption already starts or ends with it.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| caption | STRING | yes | The caption text. Several captions can be given, one per line. | default '', multiline |
| prefix | STRING | yes | Trigger word or phrase to put first. Leave empty for none. | default '' |
| suffix | STRING | yes | Trigger word or phrase to put last. Leave empty for none. | default '' |
| separator | STRING | yes | Text placed between the trigger word and the caption. | default ', ' |
| per_line | BOOLEAN | yes | On: treat every line as its own caption. Off: the whole text is one caption. | default False |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | caption = '' (empty) | PASS | STRING=str '' |
| 3 | prefix = '' (empty) | PASS | STRING=str '' |
| 4 | suffix = '' (empty) | PASS | STRING=str '' |
| 5 | separator = '' (empty) | PASS | STRING=str '' |
| 6 | per_line = True | PASS | STRING=str '' |

## Verdict

All 6 cases behaved as expected (6 passed, 0 rejected with a clear message).
