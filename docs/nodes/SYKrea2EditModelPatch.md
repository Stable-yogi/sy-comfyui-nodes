# Krea2EditModelPatch SY (`SYKrea2EditModelPatch`)

Source: `nodes/sy_krea2_edit.py`

**What it does:** Adds the in-context source picture path to a Krea 2 edit model, so the edit keeps the look of the source.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The Krea 2 model, with the edit LoRA already applied. A patched copy is returned. |  |
| source_latent | LATENT | yes | The source picture encoded by a VAE Encode node. |  |
| source_latent_b | LATENT | no | Second reference (the subject) for two-reference edit LoRAs. Scene first, subject second. |  |
| ref_boost | FLOAT | no | Pulls the result toward the last reference. 1 is off, above 1 pulls harder, below 1 loosens. | 0.0 to 1000.0, step 0.01, default 1.0 |
| ref_boost_a | FLOAT | no | Same pull for the first reference (the scene in two-reference edits). 1 is off. | 0.0 to 1000.0, step 0.01, default 1.0 |
| fit_mode | COMBO | no | How a source image fits a different output shape. Use fit; crop (legacy) is only for older weights. | one of: fit, crop (legacy) |
| ref_boost_mask | MASK | no | Optional area of the last reference to boost, for example the face. Empty means all of it. | mask [B,H,W] |
| vae | VAE | no | Recommended with source_image: lets the node fit the picture in pixels before encoding. |  |
| source_image | IMAGE | no | The source as an image (needs vae). Replaces source_latent and avoids blur from size mismatch. | picture batch [B,H,W,3] |
| source_image_b | IMAGE | no | Second reference as an image (needs vae). | picture batch [B,H,W,3] |

Outputs: `MODEL`
