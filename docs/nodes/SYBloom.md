# Bloom SY (`SYBloom`)

Source: `nodes/sy_bloom.py`

**What it does:** Adds a soft glow around the bright parts of a picture: the bright parts are blurred, tinted and laid back on top. Strength 0 leaves the picture as it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to add a glow to. | picture batch [B,H,W,3] |
| threshold | FLOAT | yes | Only parts brighter than this glow. Lower makes more of the picture glow. | 0.0 to 1.0, step 0.01, default 0.7 |
| radius | INT | yes | How far the glow spreads, in pixels. | 1 to 200, default 24 |
| strength | FLOAT | yes | How strong the glow is. 0 does nothing. | 0.0 to 2.0, step 0.01, default 0.6 |
| tint | STRING | yes | Colour of the glow as a web colour, like #fff for white or #fb6 for warm. | default '#fff' |

Outputs: `IMAGE`

## How to use

1. Connect a picture or a batch to **image**.
2. Set **threshold** to choose what glows. At 0.7 only the brightest parts glow; try 0.5 to make more of the picture glow.
3. Set **radius** for how far the glow spreads (for example 24) and **strength** for how strong it is (for example 0.6). Strength 0 does nothing.
4. Type a web colour in **tint**, for example #fb6 for a warm glow or #fff for white.
