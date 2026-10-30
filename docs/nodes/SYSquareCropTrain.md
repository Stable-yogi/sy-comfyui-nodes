# Crop Square Centre For Training SY (`SYSquareCropTrain`)

Source: `nodes/sy_square_crop_train.py`

**What it does:** Cuts the biggest square from the middle of each picture and resizes it to the size you give, ready for training.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The pictures to crop. Every picture in the batch is cropped the same way. | picture batch [B,H,W,3] |
| size | INT | yes | Width and height of the finished square in pixels. | 8 to 8192, step 8, default 1024 |
| method | COMBO | yes | How to resize. Area is best for shrinking, bicubic for enlarging. | one of: area, bicubic, bilinear, nearest |

Outputs: `IMAGE`
