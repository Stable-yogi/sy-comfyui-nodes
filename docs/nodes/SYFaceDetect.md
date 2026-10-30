# Face Detect SY (`SYFaceDetect`)

Source: `nodes/sy_face_detect.py`

**What it does:** Finds faces and makes a mask for them (box or oval). Feed the mask to Inpaint Crop SY. No face found gives an empty mask and no error.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to search for faces. | picture batch [B,H,W,3] |
| detector | COMBO | yes | Built-in needs no file. Or pick a YuNet .onnx file from models/sy_face_detect. Download: https://github.com/Stable-yogi/sy-face-model | one of: Built-in (no file needed) |
| threshold | FLOAT | yes | Higher = stricter, fewer faces. | 0.05 to 0.99, step 0.01, default 0.5 |
| min_face | INT | yes | Faces whose shorter side is smaller than this many pixels are ignored. | 8 to 1024, default 32 |
| pick | COMBO | yes | Which faces to keep: the one nearest the middle, the biggest one, or all of them. | one of: centre 1, largest 1, all |
| grow | INT | yes | Pixels added on every side of each face box (kept inside the picture). | 0 to 256, default 10 |
| shape | COMBO | yes | Mask shape: a rectangle, or an oval that fits inside the grown box. | one of: box, ellipse |

Outputs: `MASK`, `INT`, `STRING`
