# Krea2OneClick SY (`SYKrea2OneClick`)

Source: `nodes/sy_krea2_oneclick.py`

**What it does:** Krea 2 text-to-image in one node: loads the model, text encoder and VAE, applies up to 3 LoRAs, samples, optionally runs a detail pass, and returns the image.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | COMBO | yes | Krea 2 diffusion model. Safetensors works as is; GGUF needs the GGUF loader pack. | one of: (no diffusion_models found) |
| prompt | STRING | yes | Describe the image to make. Empty text is allowed for testing. | default '', multiline |
| negative | STRING | yes | Describe what to avoid. Empty is handled safely at every CFG value. | default '', multiline |
| quality | COMBO | yes | Sets steps and CFG together. Pick Custom to use custom_steps and custom_cfg. | one of: Fast (8 steps), Best (16 steps), Max (20 steps), Custom |
| size | COMBO | yes | Output size. Pick Custom to use custom_width and custom_height. | one of: Portrait 2:3 (960x1440), Portrait 2:3 big (1368x2048), Portrait 3:4 (1152x1536), Square 1:1 (1024x1024), Square 1:1 big (1536x1536), Landscape 3:2 (1440x960), Landscape 3:2 big (2048x1368), Landscape 16:9 (1536x864), Custom |
| seed | INT | yes | Random seed. The same seed and settings give the same image. | 0 to 18446744073709551615, default 0 |
| detail_pass | COMBO | yes | Optional second pass: Light uses 0.25 denoise, Full uses 0.40. | one of: Off, Light, Full |
| lora_1 | COMBO | no | First optional LoRA, applied to both the model and the text encoder. | one of: None, test_lora.safetensors |
| lora_1_strength | FLOAT | no | Strength for LoRA 1. Set to 0 to skip this slot. | -4.0 to 4.0, step 0.05, default 0.8 |
| lora_2 | COMBO | no | Second optional LoRA, applied after LoRA 1. | one of: None, test_lora.safetensors |
| lora_2_strength | FLOAT | no | Strength for LoRA 2. Set to 0 to skip this slot. | -4.0 to 4.0, step 0.05, default 0.8 |
| lora_3 | COMBO | no | Third optional LoRA, applied after LoRA 2. | one of: None, test_lora.safetensors |
| lora_3_strength | FLOAT | no | Strength for LoRA 3. Set to 0 to skip this slot. | -4.0 to 4.0, step 0.05, default 0.8 |
| text_encoder | COMBO | no | Qwen3-VL text encoder. Auto picks the best filename match; pick a file to override. | one of: auto, (no text_encoders found) |
| vae | COMBO | no | Krea 2 compatible VAE. Auto prefers Qwen Image and falls back to Wan 2.1 names. | one of: auto, test_vae.safetensors |
| custom_steps | INT | no | Sampling steps, used only when quality is Custom. | 1 to 200, default 16 |
| custom_cfg | FLOAT | no | CFG, used only when quality is Custom. | 0.0 to 20.0, step 0.1, default 2.0 |
| custom_width | INT | no | Width, used only for Custom size. Rounded down to a multiple of 8. | 64 to 8192, step 16, default 960 |
| custom_height | INT | no | Height, used only for Custom size. Rounded down to a multiple of 8. | 64 to 8192, step 16, default 1440 |
| batch_size | INT | no | Number of images made in one batch. | 1 to 16, default 1 |
| shift | FLOAT | no | Sampling shift. The measured Krea 2 default is 2.95. | 0.0 to 20.0, step 0.01, default 2.95 |
| sampler_name | COMBO | no | Sampling algorithm. Euler is the measured default for Krea 2. | one of: euler |
| scheduler | COMBO | no | Noise schedule. Simple is the measured default for Krea 2. | one of: simple |
| weight_dtype | COMBO | no | Loader dtype for safetensors. Default respects the file; GGUF ignores it. | one of: default, fp8_e4m3fn, fp8_e4m3fn_fast, fp8_e5m2 |

Outputs: `IMAGE`, `MODEL`, `CLIP`, `VAE`, `CONDITIONING`, `CONDITIONING`, `LATENT`

## How it was tested

This node was not run by the harness. Reason: NOT run end to end yet: it needs real model files. Its signature matches the older node exactly and its choice logic has script tests. A real run on the owner's ComfyUI is still to do.


## Verdict

Not run. NOT run end to end yet: it needs real model files. Its signature matches the older node exactly and its choice logic has script tests. A real run on the owner's ComfyUI is still to do.
