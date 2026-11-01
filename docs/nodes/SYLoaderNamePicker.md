# Loader Name Picker SY (`SYLoaderNamePicker`)

Source: `nodes/sy_loader_name_picker.py`

**What it does:** Pick a model file from the list and get its name as text. Nothing is loaded. The folder is checked against the name. Adds: a name_filter box (words instead of scrolling), a plain message when the file is in a different folder (for example a LoRA picked under checkpoints), the match count and an info text with the size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| folder | COMBO | yes | Which model folder the name must come from. | one of: checkpoints, loras, vae, clip, unet, upscale_models |
| name | COMBO | yes | The file name to pass on. It must exist in the chosen folder. | one of: test_model.safetensors, test_lora.safetensors, test_vae.safetensors, test_upscale_models.safetensors |
| name_filter | STRING | no | Optional. Words like 'flux dev': uses the first matching file of the folder and ignores the list. | default '' |

Outputs: `STRING`, `STRING`, `INT`, `STRING`

## How to use

1. Pick folder (checkpoints, loras, vae, clip, unet or upscale_models), then pick a file name from the list.
2. Optional: type words in name_filter, for example flux dev. The first matching file of that folder is used and the list is ignored.
3. Only the name comes out as text. Nothing is loaded. You also get a plain message when the file is in another folder than the one picked.
