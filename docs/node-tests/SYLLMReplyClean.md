# LLM Reply Clean SY (`SYLLMReplyClean`)

Source: `nodes/sy_llm_reply_clean.py`

**What it does:** Cleans a chatty text reply: removes code fences, an intro line like 'Here is...:', wrapping quotes and extra blank lines.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The reply text you want to clean. | default '', multiline |
| strip_code_fences | BOOLEAN | yes | On: remove the ``` lines and keep what is inside. | default True |
| strip_preamble | BOOLEAN | yes | On: drop a first line like 'Here is your prompt:' that ends with a colon. | default True |
| strip_wrapping_quotes | BOOLEAN | yes | On: remove quote marks that wrap the whole text. | default True |
| first_paragraph_only | BOOLEAN | yes | On: keep only the first paragraph and drop the rest. | default False |
| collapse_blank_lines | BOOLEAN | yes | On: turn several empty lines in a row into one. | default True |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str '' |
| 3 | strip_code_fences = False | PASS | STRING=str '' |
| 4 | strip_preamble = False | PASS | STRING=str '' |
| 5 | strip_wrapping_quotes = False | PASS | STRING=str '' |
| 6 | first_paragraph_only = True | PASS | STRING=str '' |
| 7 | collapse_blank_lines = False | PASS | STRING=str '' |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
