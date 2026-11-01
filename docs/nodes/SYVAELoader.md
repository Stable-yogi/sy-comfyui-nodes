# VAE Loader SY (`SYVAELoader`)

Source: `nodes/sy_vae_loader.py`

**What it does:** Loads a single VAE file from your vae folder. Refuses a LoRA, a model or a text encoder picked by mistake, and the info output gives the file size, data type and which model family the name points to.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| vae_name | COMBO | yes | The VAE file to load from the vae folder. | one of: test_vae.safetensors |

Outputs: `VAE`, `STRING`

## How to use

1. Pick the VAE file in vae_name.
2. A LoRA, model or text encoder picked by mistake is refused.
3. Connect vae to your decode node. The info output gives the file size, data type and model family.
