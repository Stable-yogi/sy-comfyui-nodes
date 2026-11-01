# Safetensors Header Info SY (`SYSafetensorsHeaderInfo`)

Source: `nodes/sy_safetensors_header_info.py`

**What it does:** Shows what is inside a .safetensors model file without loading it: tensor count, data types, parameter estimate, metadata keys. Also gives a one-line summary (looks like a LoRA, VAE, checkpoint ..., main data type, size) and the metadata values, such as what a LoRA was trained on. Lists checkpoints, loras, vae, diffusion models and text encoders.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model_file | COMBO | yes | A model file, for example loras/my_style.safetensors. Only its small header is read, so it is fast. | one of: checkpoints/test_model.safetensors, loras/test_lora.safetensors, vae/test_vae.safetensors |

Outputs: `STRING`, `STRING`, `STRING`
