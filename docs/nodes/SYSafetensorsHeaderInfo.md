# Safetensors Header Info SY (`SYSafetensorsHeaderInfo`)

Source: `nodes/sy_safetensors_header_info.py`

**What it does:** Shows what is inside a .safetensors model file (tensor count, data types, parameter estimate, metadata keys) without loading the model.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model_file | COMBO | yes | A checkpoint, LoRA or VAE file. Only its small header is read. | one of: checkpoints/test_model.safetensors, loras/test_lora.safetensors, vae/test_vae.safetensors |

Outputs: `STRING`
