# Face Detect SY (`SYFaceDetect`)

Source: `nodes/sy_face_detect.py`

**What it does:** Finds faces and makes a mask for them (box or oval). Feed the mask to Inpaint Crop SY. No face found gives an empty mask and no error.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to search for faces. | picture batch [B,H,W,3] |
| detector | COMBO | yes | Built-in needs no file. Or pick a YuNet .onnx from models/sy_face_detect (download link in the README). | one of: Built-in (no file needed) |
| threshold | FLOAT | yes | Higher = stricter, fewer faces. | 0.05 to 0.99, step 0.01, default 0.5 |
| min_face | INT | yes | Faces whose shorter side is smaller than this many pixels are ignored. | 8 to 1024, default 32 |
| pick | COMBO | yes | Which faces to keep: the one nearest the middle, the biggest one, or all of them. | one of: centre 1, largest 1, all |
| grow | INT | yes | Pixels added on every side of each face box (kept inside the picture). | 0 to 256, default 10 |
| shape | COMBO | yes | Mask shape: a rectangle, or an oval that fits inside the grown box. | one of: box, ellipse |

Outputs: `MASK`, `INT`, `STRING`

## How to use

1. Connect your picture to image.
2. Pick pick: centre 1, largest 1 or all. Set threshold and min_face.
3. Use grow to enlarge the area and shape (box or ellipse).
4. Outputs: mask, found and boxes. Feed the mask to Inpaint Crop SY. No face gives an empty mask and no error.
