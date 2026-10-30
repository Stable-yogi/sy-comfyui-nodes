# Sepia SY (`SYSepia`)

Source: `nodes/sy_sepia.py`

**What it does:** Gives a picture the warm brown tone of an old photograph. Strength blends from the original to full sepia.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | 0 keeps the original, 1 is full sepia. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `IMAGE`
