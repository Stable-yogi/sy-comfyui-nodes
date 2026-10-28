# Unet Loader SY (`SYUnetLoader`)

Source: `nodes/sy_unet_loader.py`

**What it does:** Loads a diffusion model (unet) file. The weight type can store it smaller in fp8 to save memory.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| unet_name | COMBO | yes | The diffusion model file to load. | one of: |
| weight_dtype | COMBO | yes | default keeps the type stored in the file. fp8 uses less memory. | one of: default, fp8_e4m3fn, fp8_e4m3fn_fast, fp8_e5m2 |

Outputs: `MODEL`

## How it was tested

This node was not run by the harness. Reason: run by hand with a real unet file on the processor: it loaded in 6 s and gave a model.


## Verdict

Not run. run by hand with a real unet file on the processor: it loaded in 6 s and gave a model.
