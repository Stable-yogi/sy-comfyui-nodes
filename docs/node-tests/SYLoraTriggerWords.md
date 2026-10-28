# LoRA Trigger Words SY (`SYLoraTriggerWords`)

Source: `nodes/sy_lora_trigger_words.py`

**What it does:** Reads the trigger words for a LoRA from a .json or .txt file with the same name next to it. Empty when there is none.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| lora_name | COMBO | yes | The LoRA whose trigger words you want. | one of: None, test_lora.safetensors |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '' |
| 2 | lora_name = 'test_lora.safetensors' | PASS | STRING=str 'sytest, sytwo' |

## Verdict

All 2 cases behaved as expected (2 passed, 0 rejected with a clear message).
