# Upscale SY (`SYUpscale`)

Source: `nodes/sy_upscale.py`

**What it does:** Picks an upscale model, enlarges a picture or video frames, and lands on the exact size you want (longest side, width, height or megapixels). Video frames go through in chunks, and a chunk is halved by itself if the card runs out of memory. Model on None = plain resize.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or the video frames to enlarge. | picture batch [B,H,W,3] |
| upscale_model | COMBO | yes | The upscale model file. None = plain resize only. | one of: None, test_upscale_models.safetensors |
| target | COMBO | yes | What the amount below means. 'Keep the model's size' uses the size the model gives. | one of: Keep the model's size, Longest side, Width, Height, Megapixels |
| amount | FLOAT | yes | Pixels for side, width and height. Megapixels for the last choice. | 0.0 to 32768.0, step 1.0, default 2048.0 |
| method | COMBO | yes | How the last resize to the exact size is done. | one of: lanczos, bicubic, bilinear, area, nearest-exact |
| chunk_frames | INT | yes | Frames sent through the model at once. Lower = less memory. | 1 to 512, default 8 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect the picture or the video frames to image.
2. Pick an upscale_model. None means a plain resize only.
3. Set target (keep the model's size, longest side, width, height or megapixels) and amount, then method for the last resize.
4. For video, chunk_frames sets how many frames go through the model at once. Lower uses less memory.
