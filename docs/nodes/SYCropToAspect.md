# Crop To Aspect SY (`SYCropToAspect`)

Source: `nodes/sy_crop_to_aspect.py`

**What it does:** Crops a picture to a shape such as 16:9 or 1:1. Takes the biggest area of that shape, centred or moved with the offsets. Can snap the size to a multiple of 8 or 64 and says what it took.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to crop. | picture batch [B,H,W,3] |
| aspect_w | INT | yes | Width part of the shape, the 16 in 16:9. | 1 to 1000, default 16 |
| aspect_h | INT | yes | Height part of the shape, the 9 in 16:9. | 1 to 1000, default 9 |
| offset_x | FLOAT | yes | Moves the crop sideways. -1 is left, 0 is centre, 1 is right. | -1.0 to 1.0, step 0.01, default 0.0 |
| offset_y | FLOAT | yes | Moves the crop up or down. -1 is top, 0 is centre, 1 is bottom. | -1.0 to 1.0, step 0.01, default 0.0 |
| multiple_of | INT | no | Trim the crop so width and height are multiples of this, for example 8 or 64. 1 = off. | 1 to 512, step 1, default 1 |

Outputs: `IMAGE`, `INT`, `INT`, `STRING`

## How to use

1. Connect your picture to image.
2. Set aspect_w and aspect_h, for example 16 and 9.
3. The biggest area of that shape is taken, centred. Move it with offset_x and offset_y.
4. Set multiple_of to snap the size. Outputs: image, width, height and info.
