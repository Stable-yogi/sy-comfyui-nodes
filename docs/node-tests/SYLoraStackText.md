# LoRA Stack Text SY (`SYLoraStackText`)

Source: `nodes/sy_lora_stack_text.py`

**What it does:** Writes up to 4 LoRA names and strengths as a short summary and as <lora:name:0.8> tags. It does not apply the LoRAs.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| lora_1 | COMBO | yes | LoRA for slot 1. Leave on None to skip it. | one of: None, test_lora.safetensors |
| strength_1 | FLOAT | yes | Strength for slot 1. | -20.0 to 20.0, step 0.05, default 1.0 |
| lora_2 | COMBO | yes | LoRA for slot 2. Leave on None to skip it. | one of: None, test_lora.safetensors |
| strength_2 | FLOAT | yes | Strength for slot 2. | -20.0 to 20.0, step 0.05, default 1.0 |
| lora_3 | COMBO | yes | LoRA for slot 3. Leave on None to skip it. | one of: None, test_lora.safetensors |
| strength_3 | FLOAT | yes | Strength for slot 3. | -20.0 to 20.0, step 0.05, default 1.0 |
| lora_4 | COMBO | yes | LoRA for slot 4. Leave on None to skip it. | one of: None, test_lora.safetensors |
| strength_4 | FLOAT | yes | Strength for slot 4. | -20.0 to 20.0, step 0.05, default 1.0 |

Outputs: `STRING`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 2 | lora_1 = 'test_lora.safetensors' | PASS | STRING=str '1. test_lora.safetensors (strength 1)'; STRING=str '<lora:test_lora:1>' |
| 3 | strength_1 = -20.0 (min) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 4 | strength_1 = 20.0 (max) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 5 | strength_1 = 0.0 (mid) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 6 | lora_2 = 'test_lora.safetensors' | PASS | STRING=str '1. test_lora.safetensors (strength 1)'; STRING=str '<lora:test_lora:1>' |
| 7 | strength_2 = -20.0 (min) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 8 | strength_2 = 20.0 (max) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 9 | strength_2 = 0.0 (mid) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 10 | lora_3 = 'test_lora.safetensors' | PASS | STRING=str '1. test_lora.safetensors (strength 1)'; STRING=str '<lora:test_lora:1>' |
| 11 | strength_3 = -20.0 (min) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 12 | strength_3 = 20.0 (max) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 13 | strength_3 = 0.0 (mid) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 14 | lora_4 = 'test_lora.safetensors' | PASS | STRING=str '1. test_lora.safetensors (strength 1)'; STRING=str '<lora:test_lora:1>' |
| 15 | strength_4 = -20.0 (min) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 16 | strength_4 = 20.0 (max) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |
| 17 | strength_4 = 0.0 (mid) | PASS | STRING=str 'No LoRAs selected.'; STRING=str '' |

## Verdict

All 17 cases behaved as expected (17 passed, 0 rejected with a clear message).
