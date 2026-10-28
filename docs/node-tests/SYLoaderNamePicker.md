# Loader Name Picker SY (`SYLoaderNamePicker`)

Source: `nodes/sy_loader_name_picker.py`

**What it does:** Pick a model file from the list and get its name as text. Nothing is loaded. The folder is checked against the name.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| folder | COMBO | yes | Which model folder the name must come from. | one of: checkpoints, loras, vae, clip, unet, upscale_models |
| name | COMBO | yes | The file name to pass on. It must exist in the chosen folder. | one of: |

Outputs: `STRING`, `STRING`

## How it was tested

This node was not run by the harness. Reason: skipped: the list for 'name' is filled in by the running app and is empty here.


## Verdict

Not run. skipped: the list for 'name' is filled in by the running app and is empty here.
