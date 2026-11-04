# Ref Image Size SY (`SYRefImageSize`)

Source: `nodes/sy_ref_image_size.py`

**What it does:** Puts a reference picture into the shape and size of your video before a video model reads it. Fit keeps the whole picture, fill crops it to the video shape, pad adds borders so nothing is cut. max_side keeps big pictures from slowing the model down.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The reference picture (one or a batch). | picture batch [B,H,W,3] |
| video_width | INT | yes | Width of the video you make. Wire it from your size node. | 16 to 16384, default 864 |
| video_height | INT | yes | Height of the video you make. Wire it from your size node. | 16 to 16384, default 480 |
| mode | COMBO | yes | Fit: whole picture, own shape. Fill: video shape, edges cut. Pad: video shape, borders added. Keep shape: only resize. | one of: fit inside video, fill video (crop), pad to video shape, keep shape |
| max_side | INT | no | Longest side limit in pixels. 0 = the video size. Smaller is faster and uses less memory. | 0 to 16384, default 0 |
| pad_colour | COMBO | no | Border colour for pad mode. Edge repeats the outer pixels. | one of: black, white, grey, edge |
| multiple | INT | no | Width and height are rounded to this step. 8 is safe for most models. | 1 to 64, default 8 |

Outputs: `IMAGE`, `INT`, `INT`, `STRING`

## How to use

1. Put it between your reference picture and the video model's reference input.
2. Wire video_width and video_height from the node that sets your video size, so the picture always matches the video.
3. Pick a mode. Pad to video shape keeps the whole picture and adds borders (safest for faces). Fill video crops the edges. Fit inside keeps the picture's own shape.
4. Set max_side (for example 1024) to make big pictures faster and lighter on memory. 0 uses the video size.
5. Read info: it warns when a lot of the picture is cut off, or when a tall picture goes into a wide video.
