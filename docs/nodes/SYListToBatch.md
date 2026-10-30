# List To Batch SY (`SYListToBatch`)

Source: `nodes/sy_batch_list.py`

**What it does:** Collects a list of pictures back into one batch. Pictures of other sizes can be resized to match the first.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The list of pictures to collect into one batch. | picture batch [B,H,W,3] |
| resize_to_first | BOOLEAN | no | On: resize every picture to the first one's size. Off: stop with an error when sizes differ. | default True |

Outputs: `IMAGE`, `INT`
