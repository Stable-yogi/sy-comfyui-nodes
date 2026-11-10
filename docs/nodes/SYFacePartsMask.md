# Face Parts Mask SY (`SYFacePartsMask`)

Source: `nodes/sy_face_parts_mask.py`

**What it does:** Tick the face parts you want (skin, eyes, brows, lips, hair, neck and more) and get one mask of them. It also gives a coloured map of every part it found. One node replaces the old chain of model loader, processor loader, parser and part picker.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures with a face. | picture batch [B,H,W,3] |
| background, skin, nose, glasses, left_eye, right_eye, left_brow, right_brow, left_ear, right_ear, mouth_inside, upper_lip, lower_lip, hair, hat, earring, necklace, neck, clothes | BOOLEAN | yes | On: that part goes into the mask. | default on: skin, nose, eyes, brows, mouth_inside, lips |

Outputs: `MASK` (mask), `IMAGE` (parts_map), `STRING` (info)

## Model file

Put a Segformer face-parsing model in `models/face_parsing`: `config.json`, `preprocessor_config.json` and `model.safetensors`. A missing file gives a clear error naming it.

## How to use

1. Connect your picture to image.
2. Tick the parts you want in the mask (for a skin fix: skin and nose; for lips only: upper_lip and lower_lip).
3. Use mask for inpainting or face detail; grow or blur it with Mask Grow Shrink SY or Mask Feather SY.
4. Look at parts_map to see what the model found. Nothing ticked gives an empty mask.
