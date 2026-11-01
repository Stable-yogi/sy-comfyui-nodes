# Model Loader SY (`SYModelLoader`)

Source: `nodes/sy_model_loader.py`

**What it does:** Loads a whole model in one box: the diffusion model, the text encoder(s) and the VAE. One switch changes the whole set between Safetensors and GGUF.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| format | COMBO | yes | The switch. Safetensors uses the normal files, GGUF uses the smaller GGUF files. | one of: Safetensors, GGUF |
| model_safetensors | COMBO | yes | Diffusion model used when format is Safetensors. | one of: (none) |
| model_gguf | COMBO | yes | Diffusion model used when format is GGUF. | one of: (none) |
| text_encoder | COMBO | yes | Text encoder used with Safetensors (and with GGUF if no GGUF encoder is picked). | one of: (none) |
| text_encoder_gguf | COMBO | yes | Text encoder used when format is GGUF. Leave (none) to use the normal one. | one of: (none) |
| family | COMBO | yes | The model family the text encoder belongs to. | one of: stable_diffusion, stable_cascade, sd3, stable_audio, mochi, ltxv, pixart, cosmos, lumina2, wan, hidream, chroma ... |
| vae | COMBO | yes | The VAE file. Pick (none) if you load the VAE somewhere else. | one of: test_vae.safetensors, (none) |
| text_encoder_2 | COMBO | no | A second text encoder, for models that use two. Leave (none) if not needed. | one of: (none) |
| audio_vae | COMBO | no | A second VAE for sound, used by video models with audio. Leave (none) otherwise. | one of: (none), test_vae.safetensors |
| weight_dtype | COMBO | no | Safetensors only. fp8 stores the model smaller. GGUF ignores this. | one of: default, fp8_e4m3fn, fp8_e4m3fn_fast, fp8_e5m2 |

Outputs: `MODEL`, `CLIP`, `VAE`, `VAE`, `STRING`

## How to use

1. Choose format: Safetensors or GGUF. This one switch changes the whole set.
2. Pick the diffusion model in model_safetensors or model_gguf, the text_encoder (and text_encoder_gguf for GGUF), the family it belongs to, and the vae.
3. Optional: text_encoder_2 for models that use two, audio_vae for video with sound, weight_dtype (fp8 is smaller, Safetensors only).
Outputs: model, clip, vae, audio_vae and an info line.
