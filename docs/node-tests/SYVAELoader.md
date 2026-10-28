# VAE Loader SY (`SYVAELoader`)

Source: `nodes/sy_vae_loader.py`

**What it does:** Loads a single VAE file from your vae folder.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| vae_name | COMBO | yes | The VAE file to load from the vae folder. | one of: test_vae.safetensors |

Outputs: `VAE`

## How it was tested

This node was not run by the harness. Reason: run by hand with a real 160 MB VAE file on the processor: it loaded in 14 s and gave a VAE.


## Verdict

Not run. run by hand with a real 160 MB VAE file on the processor: it loaded in 14 s and gave a VAE.
