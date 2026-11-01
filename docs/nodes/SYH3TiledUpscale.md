# H3 Tiled Upscale SY (`SYH3TiledUpscale`)

Source: `nodes/sy_h3_tiled_upscale.py`

**What it does:** Enlarges a big picture or video frames with an upscale model in overlapping tiles, so the card never runs out of memory. Tiles are blended softly so no seams show. If memory still runs short, the tile size is halved by itself and the run continues.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or the video frames to enlarge. | picture batch [B,H,W,3] |
| upscale_model | COMBO | yes | The upscale model file. | one of: test_upscale_models.safetensors |
| tile_size | INT | no | Size of one input tile in pixels. Smaller uses less memory. | 128 to 2048, step 8, default 512 |
| overlap | INT | no | Pixels shared by neighbour tiles. 32 to 64 hides the seams. | 0 to 256, default 32 |
| blend | COMBO | no | feather mixes the overlaps softly. none just pastes the tiles. | one of: feather, none |
| target | COMBO | no | What the amount means. 'Keep the model's size' uses the size the model gives. | one of: Keep the model's size, Longest side, Width, Height, Megapixels |
| amount | FLOAT | no | Pixels for side, width and height. Megapixels for the last choice. | 0.0 to 32768.0, step 1.0, default 2048.0 |
| method | COMBO | no | How the last resize to the exact size is done. | one of: lanczos, bicubic, bilinear, area, nearest-exact |
| auto_retry | BOOLEAN | no | If memory runs out, halve the tile size (down to 128) and go on. | default True |
| chunk_frames | INT | no | Frames sent through the model at once. Lower = less memory. | 1 to 64, default 4 |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect the picture or video frames to image and pick the upscale_model.
2. Set tile_size (smaller uses less memory) and overlap (32 to 64 hides seams). blend feather mixes the overlaps softly.
3. Use target and amount to reach an exact size, or leave Keep the model's size. method sets the final resize.
4. Keep auto_retry on: if memory runs out, the tile size is halved (down to 128) and the run goes on. Lower chunk_frames to use less memory.
5. The enlarged picture and an info line come out.
