# Loader Name Picker SY (`SYLoaderNamePicker`)

Source: `nodes/sy_loader_name_picker.py`

**What it does:** Pick a model file from the list and get its name as text. Nothing is loaded. The folder is checked against the name.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| folder | COMBO | yes | Which model folder the name must come from. | one of: checkpoints, loras, vae, clip, unet, upscale_models |
| name | COMBO | yes | The file name to pass on. It must exist in the chosen folder. | one of: test_model.safetensors, test_lora.safetensors, test_vae.safetensors, test_upscale_models.safetensors |

Outputs: `STRING`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'test_model.safetensors'; STRING=str 'test_model' |
| 2 | folder = 'loras' | REJECTED | ValueError: 'test_model.safetensors' is not in the loras list. Refresh the list or pick a... |
| 3 | folder = 'vae' | REJECTED | ValueError: 'test_model.safetensors' is not in the vae list. Refresh the list or pick ano... |
| 4 | folder = 'clip' | REJECTED | ValueError: no files found in the clip folder. Put a model file there and refresh the list |
| 5 | folder = 'unet' | REJECTED | ValueError: no files found in the unet folder. Put a model file there and refresh the list |
| 6 | folder = 'upscale_models' | REJECTED | ValueError: 'test_model.safetensors' is not in the upscale_models list. Refresh the list ... |
| 7 | name = 'test_lora.safetensors' | REJECTED | ValueError: 'test_lora.safetensors' is not in the checkpoints list. Refresh the list or p... |
| 8 | name = 'test_vae.safetensors' | REJECTED | ValueError: 'test_vae.safetensors' is not in the checkpoints list. Refresh the list or pi... |
| 9 | name = 'test_upscale_models.safetensors' | REJECTED | ValueError: 'test_upscale_models.safetensors' is not in the checkpoints list. Refresh the... |

Note: this node refuses on purpose here (refuses a file name that is not in the chosen folder's list, with a clear message), so a plain-words refusal in any case is counted as REJECTED.


## Verdict

All 9 cases behaved as expected (1 passed, 8 rejected with a clear message).
