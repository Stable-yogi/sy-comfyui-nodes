# LoRA Stack Text SY (`SYLoraStackText`)

Source: `nodes/sy_lora_stack_text.py`

**What it does:** Writes up to 4 LoRA names and strengths as a short summary and as <lora:name:0.8> tags. It does not apply the LoRAs. Gives the count, can leave out strength-0 slots, and warns when a LoRA is picked twice or the total is very high.

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
| skip_zero | BOOLEAN | no | On: a slot with strength 0 is left out of the text. | default False |

Outputs: `STRING`, `STRING`, `INT`, `STRING`

## How to use

1. Pick up to 4 LoRAs and give each a strength.
2. Turn skip_zero on to leave out slots with strength 0.
3. Read the text outputs: a short summary, the same list as <lora:name:0.8> tags, and a warning text. The number output is the count of LoRAs listed.
Note: this node only writes text. It does not apply any LoRA to a model.
