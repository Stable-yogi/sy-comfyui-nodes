# H3SaveBundle SY (`SYH3SaveBundle`)

Source: `nodes/sy_h3_bundle.py`

**What it does:** Saves a latent, its prompt, seed and up to 3 reference pictures into one folder in the output folder.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| latent | LATENT | yes | The latent to keep. Every tensor in it is saved. |  |
| prompt | STRING | yes | The prompt text that made this latent. | default '' |
| seed | INT | yes | The seed that made this latent. | 0 to 18446744073709551615 |
| bundle_name | STRING | yes | Folder name in output/sy_bundles. Same name overwrites that bundle. | default 'h3-preview-001' |
| reference_1 | IMAGE | no | Optional picture saved as ref_1.png (first picture of the batch). | picture batch [B,H,W,3] |
| reference_2 | IMAGE | no | Optional picture saved as ref_2.png (first picture of the batch). | picture batch [B,H,W,3] |
| reference_3 | IMAGE | no | Optional picture saved as ref_3.png (first picture of the batch). | picture batch [B,H,W,3] |

Outputs: `STRING`
