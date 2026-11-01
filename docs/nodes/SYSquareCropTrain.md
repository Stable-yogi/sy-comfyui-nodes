# Crop Square Centre For Training SY (`SYSquareCropTrain`)

Source: `nodes/sy_square_crop_train.py`

**What it does:** Cuts the biggest square from the middle of each picture and resizes it to the size you give, ready for training. Anchor picks which part of a long picture is kept (top keeps heads). The info output says the crop and warns when a small picture is enlarged a lot.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures to crop. Every picture in the batch is cropped the same way. | picture batch [B,H,W,3] |
| size | INT | yes | Width and height of the finished square in pixels. | 8 to 8192, step 8, default 1024 |
| method | COMBO | yes | How to resize. Area is best for shrinking, bicubic for enlarging. | one of: area, bicubic, bilinear, nearest |
| anchor | COMBO | no | Which part is kept: top for portraits (heads), left/right for wide pictures, top_left for both. | one of: centre, top_left, top, bottom, left, right |

Outputs: `IMAGE`, `STRING`
