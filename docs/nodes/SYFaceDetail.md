# FaceDetail SY (`SYFaceDetail`)

Source: `nodes/sy_face_detail.py`

**What it does:** Finds each face, redraws it bigger with a short second pass of the sampler, and blends it back softly. No face found leaves the picture as it is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures whose faces should get more detail. | picture batch [B,H,W,3] |
| model | MODEL | yes | The model used to redraw each face. |  |
| vae | VAE | yes | Turns the face crop into latent data and back into a picture. |  |
| positive | CONDITIONING | yes | What the redrawn face should look like. |  |
| negative | CONDITIONING | yes | What the redrawn face should avoid. |  |
| detector | COMBO | yes | Built-in needs no file. Or pick a YuNet .onnx from models/sy_face_detect. | one of: Built-in (no file needed) |
| pick | COMBO | yes | Which faces to redraw: the biggest one, the one nearest the middle, or all. | one of: centre 1, largest 1, all |
| crop_size | INT | yes | The size in pixels each face is redrawn at. | 256 to 2048, step 64, default 768 |
| padding | FLOAT | yes | Extra picture around the face, as a fraction of the face box. | 0.0 to 2.0, step 0.05, default 0.5 |
| denoise | FLOAT | yes | How much the face is changed. Low keeps the face, high redraws it. | 0.0 to 1.0, step 0.01, default 0.35 |
| steps | INT | yes | Number of sampling steps for each face. | 1 to 200, default 20 |
| cfg | FLOAT | yes | How strongly the sampler follows the prompt. | 0.0 to 100.0, step 0.1, default 6.0 |
| sampler_name | COMBO | yes | The sampling method. | one of: euler, euler_ancestral, dpmpp_2m, dpmpp_sde, uni_pc |
| scheduler | COMBO | yes | How the noise steps are spread. | one of: normal, karras, simple, sgm_uniform, beta |
| seed | INT | yes | Random seed. Each face after the first uses the seed plus its number. | 0 to 18446744073709551615, default 0 |
| feather | INT | yes | Soft edge in pixels where the new face blends into the old picture. | 0 to 128, default 24 |
| min_face | INT | yes | Faces whose shorter side is smaller than this many pixels are ignored. | 16 to 512, default 48 |
| mask | MASK | no | Optional. Only change the white area of this mask. | mask [B,H,W] |

Outputs: `IMAGE`, `IMAGE`, `MASK`, `INT`, `STRING`
