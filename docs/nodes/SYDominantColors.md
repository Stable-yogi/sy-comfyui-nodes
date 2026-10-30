# Dominant Colors SY (`SYDominantColors`)

Source: `nodes/sy_dominant_colors.py`

**What it does:** Finds the main colours of a picture. Gives a text list of hex colours and a strip of colour swatches.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to read. Only the first picture of a batch is used. | picture batch [B,H,W,3] |
| count | INT | yes | How many main colours to find. | 1 to 12, default 5 |
| sample_size | INT | yes | The picture is shrunk to this longest side first. Bigger is slower. | 16 to 512, default 128 |

Outputs: `STRING`, `IMAGE`
