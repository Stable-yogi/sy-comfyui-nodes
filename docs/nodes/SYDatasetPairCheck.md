# Dataset Pair Check SY (`SYDatasetPairCheck`)

Source: `nodes/sy_dataset_pair_check.py`

**What it does:** Checks that the number of pictures equals the number of caption lines, says which pictures or lines are left over, lists empty caption lines and can warn about repeated captions. Also gives the caption count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| captions | STRING | yes | All captions, one caption per line. | default '', multiline |
| image_count | INT | yes | Number of pictures. Ignored when a picture batch is connected. | 0 to 10000000, default 0 |
| skip_blank_lines | BOOLEAN | yes | On: empty caption lines are not counted. Off: each one counts as a caption. | default False |
| images | IMAGE | no | Optional picture batch. When connected, its size is used as the picture count. | picture batch [B,H,W,3] |
| warn_duplicates | BOOLEAN | no | On: also warn when two captions are the same (capitals and spaces ignored). | default False |

Outputs: `BOOLEAN`, `STRING`, `INT`

## How to use

1. Paste the captions in captions, one per line.
2. Set image_count, or connect the pictures to images.
3. Turn on skip_blank_lines to ignore empty lines, and warn_duplicates to flag repeated captions.
4. Outputs: match (true or false), a report of leftover pictures or lines, and caption_count.
