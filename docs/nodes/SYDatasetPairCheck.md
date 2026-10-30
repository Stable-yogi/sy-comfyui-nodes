# Dataset Pair Check SY (`SYDatasetPairCheck`)

Source: `nodes/sy_dataset_pair_check.py`

**What it does:** Checks that the number of pictures equals the number of caption lines, and lists empty caption lines.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| captions | STRING | yes | All captions, one caption per line. | default '', multiline |
| image_count | INT | yes | Number of pictures. Ignored when a picture batch is connected. | 0 to 10000000, default 0 |
| skip_blank_lines | BOOLEAN | yes | On: empty caption lines are not counted. Off: each one counts as a caption. | default False |
| images | IMAGE | no | Optional picture batch. When connected, its size is used as the picture count. | picture batch [B,H,W,3] |

Outputs: `BOOLEAN`, `STRING`
