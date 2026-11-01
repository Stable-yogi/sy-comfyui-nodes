# Dominant Colors SY (`SYDominantColors`)

Source: `nodes/sy_dominant_colors.py`

**What it does:** Finds the main colours of a picture. Gives a text list of hex colours, a strip of colour swatches and how much of the picture each colour covers. Can read any picture of a batch and ignore the area outside a mask.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to read. Only the first picture of a batch is used. | picture batch [B,H,W,3] |
| count | INT | yes | How many main colours to find. | 1 to 12, default 5 |
| sample_size | INT | yes | The picture is shrunk to this longest side first. Bigger is slower. | 16 to 512, default 128 |
| mask | MASK | no | Optional. Only the white part of the mask is read, for example the subject without the background. | mask [B,H,W] |
| picture_number | INT | no | Which picture of a batch to read, counting from 0. The default is the first. | 0 to 4095, default 0 |

Outputs: `STRING`, `IMAGE`, `STRING`
