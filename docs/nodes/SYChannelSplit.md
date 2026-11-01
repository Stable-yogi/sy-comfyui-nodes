# Channel Split SY (`SYChannelSplit`)

Source: `nodes/sy_channel_split.py`

**What it does:** Splits a picture into four masks: red, green, blue and alpha (transparency). Alpha is all ones if the picture has none. Also gives a brightness (luma) mask.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to split. Outputs are red, green, blue and alpha masks. | picture batch [B,H,W,3] |

Outputs: `MASK`, `MASK`, `MASK`, `MASK`, `MASK`

## How to use

1. Connect your picture to image.
2. You get four masks: red, green, blue and alpha (all ones if the picture has no transparency).
3. A brightness (luma) mask also comes out.
