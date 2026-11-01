# Image Blend SY (`SYImageBlend`)

Source: `nodes/sy_image_blend.py`

**What it does:** Lays one picture over another. Pick a blend mode and how strong the top picture is. A top picture of another size is stretched, or scaled to cover and cropped. A mask limits where it shows, and the top picture's transparency can be used.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| base | IMAGE | yes | The bottom picture. The result has its size. | picture batch [B,H,W,3] |
| top | IMAGE | yes | The picture laid over the base. It is resized to the base size when needed. | picture batch [B,H,W,3] |
| mode | COMBO | yes | How the two pictures mix. Normal just shows the top picture. | one of: normal, multiply, screen, overlay, add, difference |
| opacity | FLOAT | yes | How strong the top picture is. 0 shows only the base, 1 the full mix. | 0.0 to 1.0, step 0.01, default 0.5 |
| top_fit | COMBO | no | If the top picture has another size: stretch it, or fill and crop (keeps its shape). | one of: stretch, fill and crop |
| use_top_alpha | BOOLEAN | no | On: transparent parts of the top picture (if it has transparency) let the base show through. | default False |
| mask | MASK | no | Optional. The top picture shows only where this mask is white. A different size is stretched to fit. | mask [B,H,W] |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect the bottom picture to base and the picture to lay over it to top. The result has the size of base.
2. Pick mode (normal, multiply, screen, overlay, add or difference) and set opacity. 0 shows only the base.
3. If top has another size, top_fit either stretches it or fills and crops it. Turn on use_top_alpha to let the base show through transparent parts of top.
4. Optional: connect a mask. The top picture shows only where it is white. The result and an info line come out.
