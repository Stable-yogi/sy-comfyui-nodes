# Image Info SY (`SYImageInfo`)

Source: `nodes/sy_image_info.py`

**What it does:** Passes the image through and tells you its width, height, batch size and megapixels. Also gives the shape (4:3, 16:9 ...), the colour channels, and an info line that warns about sizes most models dislike.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to measure. It passes through unchanged. | picture batch [B,H,W,3] |

Outputs: `IMAGE`, `INT`, `INT`, `INT`, `FLOAT`, `INT`, `STRING`, `STRING`

## How to use

1. Connect a picture to image. It passes through unchanged.
2. You get its width, height, batch size and megapixels, then the shape (like 4:3 or 16:9), the colour channels, and an info line that warns about sizes most models dislike.
