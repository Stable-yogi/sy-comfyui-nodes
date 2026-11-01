# Lora Loader Stack SY (`SYLoraLoaderStack`)

Source: `nodes/sy_lora_loader_stack.py`

**What it does:** Applies up to 4 LoRAs to the model and clip. Slots on None or with strength 0 are skipped. Adds: a bypass switch (compare with and without LoRAs without rewiring), a clip_scale (0 = change only the model), trigger words or common training tags read from the LoRA files, and a warning for a LoRA used twice.

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
| bypass | BOOLEAN | no | On = pass model and clip on without any LoRA. Handy to compare. | default False |
| clip_scale | FLOAT | no | Clip strength = strength x this. 1 = same as before, 0 = model only. | 0.0 to 4.0, step 0.05, default 1.0 |

Outputs: `MODEL`, `CLIP`, `STRING`, `STRING`, `STRING`

## How to use

1. Connect model and clip.
2. Pick up to 4 LoRAs in lora_1 to lora_4 and set a strength for each. A slot on None or with strength 0 is skipped.
3. Turn bypass on to compare the result with no LoRAs, without rewiring. Set clip_scale to 0 if the LoRAs should change only the model.
4. Use the model and clip outputs further on. The text outputs give trigger words or tags and any warning, for example when a LoRA is used twice.
