# RTX Upscale SY (`SYRtxUpscale`)

Source: `nodes/sy_rtx_upscale.py`

**What it does:** Makes a picture or video bigger with the NVIDIA RTX upscaler. Pick a target like 4K instead of working out a factor, and get a plain message if the RTX pack or card is missing instead of a red error.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or video frames to enlarge. | picture batch [B,H,W,3] |
| target | COMBO | yes | How big the result should be. 4K = 2160 pixels high, the width follows. | one of: 2x bigger, 3x bigger, 4x bigger, Height 1440 (QHD), Height 2160 (4K), Height 4320 (8K) |
| quality | COMBO | yes | ULTRA keeps the most detail and is the slowest. | one of: LOW, MEDIUM, HIGH, ULTRA |
| strength | FLOAT | yes | How strong the effect is. 1 is the default. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect your picture or video frames to image.
2. Choose target: a factor such as 2x bigger, or a height such as 4K (2160 pixels high, the width follows).
3. Choose quality (ULTRA keeps the most detail and is the slowest) and strength (1 is the default).
If the RTX pack or card is missing you get a plain message in the info output instead of a red error.
