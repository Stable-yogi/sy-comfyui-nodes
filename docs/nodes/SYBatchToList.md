# Batch To List SY (`SYBatchToList`)

Source: `nodes/sy_batch_list.py`

**What it does:** Turns one batch into a list of single pictures, so the nodes after it run once per picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch to split into single pictures. | picture batch [B,H,W,3] |

Outputs: `IMAGE`
