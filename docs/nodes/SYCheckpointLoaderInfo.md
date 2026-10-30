# Checkpoint Loader Info SY (`SYCheckpointLoaderInfo`)

Source: `nodes/sy_checkpoint_loader_info.py`

**What it does:** Loads a checkpoint from your checkpoints folder. Also gives a text line with the file name and size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| ckpt_name | COMBO | yes | The checkpoint file to load from the checkpoints folder. | one of: test_model.safetensors |

Outputs: `MODEL`, `CLIP`, `VAE`, `STRING`
