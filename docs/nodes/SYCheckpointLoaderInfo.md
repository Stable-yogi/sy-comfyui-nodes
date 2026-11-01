# Checkpoint Loader Info SY (`SYCheckpointLoaderInfo`)

Source: `nodes/sy_checkpoint_loader_info.py`

**What it does:** Loads a checkpoint like the plain loader, and adds: a name_filter box (type part of a name instead of scrolling a long list), a plain info text (size, format, fp8/fp16 explained), warnings for a wrong or empty file, and the name of the file that was really loaded.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| ckpt_name | COMBO | yes | The checkpoint file to load from the checkpoints folder. | one of: test_model.safetensors |
| name_filter | STRING | no | Optional. Words like 'flux dev': loads the first matching file and ignores the list. | default '' |

Outputs: `MODEL`, `CLIP`, `VAE`, `STRING`, `STRING`

## How to use

1. Pick the file in ckpt_name, or type part of a name in name_filter instead of scrolling.
2. The checkpoint loads like the plain loader.
3. You get model, clip and vae, an info text (size, format), warnings for a wrong or empty file, and ckpt_name, the file that was really loaded.
