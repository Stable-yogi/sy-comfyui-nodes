# Checkpoint Loader Info SY (`SYCheckpointLoaderInfo`)

Source: `nodes/sy_checkpoint_loader_info.py`

**What it does:** Loads a checkpoint from your checkpoints folder. Also gives a text line with the file name and size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| ckpt_name | COMBO | yes | The checkpoint file to load from the checkpoints folder. | one of: |

Outputs: `MODEL`, `CLIP`, `VAE`, `STRING`

## How it was tested

This node was not run by the harness. Reason: skipped: the list for 'ckpt_name' is filled in by the running app and is empty here.


## Verdict

Not run. skipped: the list for 'ckpt_name' is filled in by the running app and is empty here.
