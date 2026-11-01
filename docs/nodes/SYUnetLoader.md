# Unet Loader SY (`SYUnetLoader`)

Source: `nodes/sy_unet_loader.py`

**What it does:** Loads a diffusion model (unet) file. The weight type can store it smaller in fp8 to save memory. Checks the file first: a LoRA picked by mistake is refused in plain words, and the info output says what the file holds, its size and how it was loaded.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| unet_name | COMBO | yes | The diffusion model file to load. | one of: |
| weight_dtype | COMBO | yes | default keeps the type stored in the file. fp8 uses less memory. | one of: default, fp8_e4m3fn, fp8_e4m3fn_fast, fp8_e5m2 |

Outputs: `MODEL`, `STRING`

## How to use

1. Pick the diffusion model file in unet_name.
2. Set weight_dtype: default keeps the stored type, fp8 choices use less memory.
3. The file is checked first. A LoRA picked by mistake is refused in plain words.
4. Connect model to your sampler. The info output describes the file.
