# Checkpoint Loader Info SY (`SYCheckpointLoaderInfo`)

Source: `nodes/sy_checkpoint_loader_info.py`

**What it does:** Loads a checkpoint from your checkpoints folder. Also gives a text line with the file name and size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| ckpt_name | COMBO | yes | The checkpoint file to load from the checkpoints folder. | one of: test_model.safetensors |

Outputs: `MODEL`, `CLIP`, `VAE`, `STRING`

## How it was tested

This node was not run by the harness. Reason: run by hand with a real 6.5 GB SDXL checkpoint on the processor: 162 s, gave the model, CLIP, VAE and the info text.


## Verdict

Not run. run by hand with a real 6.5 GB SDXL checkpoint on the processor: 162 s, gave the model, CLIP, VAE and the info text.
