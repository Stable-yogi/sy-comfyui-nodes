# H3LoadBundle SY (`SYH3LoadBundle`)

Source: `nodes/sy_h3_bundle.py`

**What it does:** Loads a bundle made by H3 Save Bundle: the latent, prompt, seed, folder path and the first reference picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| bundle | COMBO | yes | A saved bundle folder from output/sy_bundles. | one of: (none) |

Outputs: `LATENT`, `STRING`, `INT`, `STRING`, `IMAGE`

## How to use

1. Pick a saved bundle folder in bundle. It lists folders from output/sy_bundles made by H3 Save Bundle.
2. The node gives back the latent, the prompt, the seed, the folder path and the first reference picture.
