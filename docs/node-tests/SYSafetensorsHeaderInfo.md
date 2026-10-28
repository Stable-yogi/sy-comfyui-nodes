# Safetensors Header Info SY (`SYSafetensorsHeaderInfo`)

Source: `nodes/sy_safetensors_header_info.py`

**What it does:** Shows what is inside a .safetensors model file (tensor count, data types, parameter estimate, metadata keys) without loading the model.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model_file | COMBO | yes | A checkpoint, LoRA or VAE file. Only its small header is read. | one of: checkpoints/test_model.safetensors, loras/test_lora.safetensors, vae/test_vae.safetensors |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'Tensors: 1 Parameters (estimate from shapes): 1 (about 0.00 billion) File siz...' |
| 2 | model_file = 'loras/test_lora.safetensors' | PASS | STRING=str 'Tensors: 1 Parameters (estimate from shapes): 1 (about 0.00 billion) File siz...' |
| 3 | model_file = 'vae/test_vae.safetensors' | PASS | STRING=str 'Tensors: 1 Parameters (estimate from shapes): 1 (about 0.00 billion) File siz...' |

## Verdict

All 3 cases behaved as expected (3 passed, 0 rejected with a clear message).
