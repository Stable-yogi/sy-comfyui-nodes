# Load Image Mini SY (`SYLoadImageMini`)

Source: `nodes/sy_load_image_mini.py`

**What it does:** Loads one picture from the ComfyUI input folder. Gives the image, its mask and its size.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | COMBO | yes | The picture file in the ComfyUI input folder. | one of: example.png |

Outputs: `IMAGE`, `MASK`, `INT`, `INT`
