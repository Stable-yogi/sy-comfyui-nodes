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
