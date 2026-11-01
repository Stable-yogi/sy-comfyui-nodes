# Load Image Mini SY (`SYLoadImageMini`)

Source: `nodes/sy_load_image_mini.py`

**What it does:** Loads one picture from the ComfyUI input folder. Gives the image, its mask and its size. Can trim it to a multiple of 8 or 64, or cap its megapixels. Finds the file even if the capital letters differ.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | COMBO | yes | The picture file in the ComfyUI input folder. | one of: example.png |
| crop_to_multiple | INT | no | Trim the edges so width and height are multiples of this (8 or 64 suit most models). 1 is off. | 1 to 512, default 1 |
| max_megapixels | FLOAT | no | Shrink a picture bigger than this many megapixels, keeping its shape. 0 is off. | 0.0 to 268.0, step 0.1, default 0.0 |

Outputs: `IMAGE`, `MASK`, `INT`, `INT`, `STRING`

## How to use

1. Pick the picture file from the input folder.
2. Optional: crop_to_multiple trims the edges so width and height are multiples of 8 or 64 (1 is off). max_megapixels shrinks a bigger picture and keeps its shape (0 is off).
3. The picture, its mask, its width and height, and an info line come out. The file is found even if the capital letters differ.
