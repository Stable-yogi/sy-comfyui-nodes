# Lora Loader Stack SY (`SYLoraLoaderStack`)

Source: `nodes/sy_lora_loader_stack.py`

**What it does:** Applies up to 4 LoRAs to the model and clip. Slots on None or with strength 0 are skipped.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The model to add LoRAs to. |  |
| clip | CLIP | yes | The text encoder (clip) to add LoRAs to. |  |
| lora_1 | COMBO | yes | LoRA for slot 1. Leave on None to skip it. | one of: None, test_lora.safetensors |
| strength_1 | FLOAT | yes | Strength for slot 1, used for model and clip. 0 skips it. | -20.0 to 20.0, step 0.05, default 1.0 |
| lora_2 | COMBO | yes | LoRA for slot 2. Leave on None to skip it. | one of: None, test_lora.safetensors |
| strength_2 | FLOAT | yes | Strength for slot 2, used for model and clip. 0 skips it. | -20.0 to 20.0, step 0.05, default 1.0 |
| lora_3 | COMBO | yes | LoRA for slot 3. Leave on None to skip it. | one of: None, test_lora.safetensors |
| strength_3 | FLOAT | yes | Strength for slot 3, used for model and clip. 0 skips it. | -20.0 to 20.0, step 0.05, default 1.0 |
| lora_4 | COMBO | yes | LoRA for slot 4. Leave on None to skip it. | one of: None, test_lora.safetensors |
| strength_4 | FLOAT | yes | Strength for slot 4, used for model and clip. 0 skips it. | -20.0 to 20.0, step 0.05, default 1.0 |

Outputs: `MODEL`, `CLIP`, `STRING`

## How it was tested

This node was not run by the harness. Reason: run by hand in a real graph on the processor (2026-10-28): a real 6.5 GB SDXL checkpoint, two real LoRAs (0.6 and 0.4) gave 722 patches on the model and a patched CLIP, the original model stayed untouched, all-zero or None slots changed nothing, and a wrong file name was refused in plain words.


## Verdict

Not run. run by hand in a real graph on the processor (2026-10-28): a real 6.5 GB SDXL checkpoint, two real LoRAs (0.6 and 0.4) gave 722 patches on the model and a patched CLIP, the original model stayed untouched, all-zero or None slots changed nothing, and a wrong file name was refused in plain words.
