# Emboss SY (`SYEmboss`)

Source: `nodes/sy_emboss.py`

**What it does:** Turns a picture into a grey relief, as if pressed into metal. The angle sets where the light comes from.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to change. | picture batch [B,H,W,3] |
| strength | FLOAT | yes | How deep the relief looks. 0 gives flat grey. | 0.0 to 10.0, step 0.1, default 1.0 |
| angle | COMBO | yes | The side the light comes from. | one of: top_left, top, top_right, left, right, bottom_left, bottom, bottom_right |

Outputs: `IMAGE`
