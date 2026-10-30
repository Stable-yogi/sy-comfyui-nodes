# Image Batch Split Every N SY (`SYImageBatchSplitEveryN`)

Source: `nodes/sy_image_batch_split_every_n.py`

**What it does:** Cuts a batch into slices of N pictures and gives you slice number K. The last slice may be shorter.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to cut. | picture batch [B,H,W,3] |
| part_size | INT | yes | How many pictures go in each slice. | 1 to 100000, default 16 |
| part | INT | yes | Which slice to output, counting from 0. | 0 to 100000, default 0 |

Outputs: `IMAGE`, `INT`, `INT`
