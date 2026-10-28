# JSON From Reply SY (`SYJSONFromReply`)

Source: `nodes/sy_json_from_reply.py`

**What it does:** Finds the first {...} or [...] in a text reply, fixes trailing commas, and gives clean compact JSON.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The reply that contains JSON somewhere inside it. | default '', multiline |
| sorted_keys | BOOLEAN | yes | On: sort the keys of every object alphabetically. | default False |
| raise_if_missing | BOOLEAN | yes | On: stop with an error if no JSON is found. Off: give empty text and found = false. | default True |

Outputs: `STRING`, `BOOLEAN`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: no valid JSON object or list found in the text. Check the reply, or turn off ... |
| 2 | text = '' (empty) | REJECTED | ValueError: no valid JSON object or list found in the text. Check the reply, or turn off ... |
| 3 | sorted_keys = True | REJECTED | ValueError: no valid JSON object or list found in the text. Check the reply, or turn off ... |
| 4 | raise_if_missing = False | PASS | STRING=str ''; BOOLEAN=bool False |

Note: this node refuses on purpose here (refuses text that holds no JSON (the sample text has none) unless raise_if_missing is off), so a plain-words refusal in any case is counted as REJECTED.


## Verdict

All 4 cases behaved as expected (1 passed, 3 rejected with a clear message).
