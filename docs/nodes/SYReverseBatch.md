# Reverse Batch SY (`SYReverseBatch`)

Source: `nodes/sy_reverse_batch.py`

**What it does:** Turns a batch of pictures around so the last one comes first. Handy for playing a video backwards.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of pictures or video frames to reverse. | picture batch [B,H,W,3] |

Outputs: `IMAGE`
