# Image Batch Split Every N SY (`SYImageBatchSplitEveryN`)

Source: `nodes/sy_image_batch_split_every_n.py`

**What it does:** Cuts a batch into slices of N pictures and gives you slice number K. The last slice may be shorter. Optional wrap goes round to slice 0 instead of failing when part is too big. Optional last_slice can pad the short last slice (repeating its last picture) or drop it. An info line says which pictures you got.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures to cut. | picture batch [B,H,W,3] |
| part_size | INT | yes | How many pictures go in each slice. | 1 to 100000, default 16 |
| part | INT | yes | Which slice to output, counting from 0. | 0 to 100000, default 0 |
| wrap | BOOLEAN | no | On: a part number that is too big goes round to the start instead of failing. | default False |
| last_slice | COMBO | no | keep leaves a short last slice short. pad fills it up. drop removes it. | one of: keep, pad, drop |

Outputs: `IMAGE`, `INT`, `INT`, `INT`, `STRING`
