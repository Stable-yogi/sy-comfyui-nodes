# Image Resize SY (`SYImageResize`)

Source: `nodes/sy_image_resize.py`

**What it does:** Changes the size of a picture. Stretch, fit inside the box, fill the box and crop the extra, or pad the gaps with a colour. Can refuse to enlarge or shrink, cap the megapixels, and resize a mask with the picture. The info line tells the scale.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to resize. | picture batch [B,H,W,3] |
| width | INT | yes | Wanted width in pixels. | 1 to 16384, default 1024 |
| height | INT | yes | Wanted height in pixels. | 1 to 16384, default 1024 |
| mode | COMBO | yes | How the picture meets the wanted size. Fit inside keeps the shape and may end smaller. | one of: stretch, fit inside, fill and crop, pad |
| multiple_of | INT | yes | Makes the result width and height a multiple of this number. 1 means off. | 1 to 512, default 8 |
| interpolation | COMBO | yes | Smoothing method. Area is good for shrinking, nearest-exact keeps hard pixels. | one of: bilinear, bicubic, area, nearest-exact |
| pad_color | COMBO | yes | Colour of the bars when the mode is pad. | one of: black, white, grey, red, green, blue |
| custom_color | STRING | no | Optional own colour as red,green,blue numbers 0 to 255, for example 200,120,40. Empty uses the list. | default '' |
| scale_limit | COMBO | no | never enlarge / never shrink: leave the picture as it is when the resize would go that way. | one of: any, never enlarge, never shrink |
| max_megapixels | FLOAT | no | Lower the wanted size until the result is at most this many megapixels. 0 is off. | 0.0 to 268.0, step 0.1, default 0.0 |
| mask | MASK | no | Optional mask that is resized together with the picture, so the two stay matched. | mask [B,H,W] |
| pad_area_in_mask | COMBO | no | In pad mode: should the new bars count as masked (1) or not (0) in the mask output. | one of: not masked (0), masked (1) |

Outputs: `IMAGE`, `INT`, `INT`, `MASK`, `STRING`

## How to use

1. Connect a picture or batch to image and set the wanted width and height.
2. Pick mode: stretch, fit inside (keeps the shape and may end smaller), fill and crop, or pad (bars of pad_color or a custom_color).
3. multiple_of makes the result a multiple of that number (1 is off). scale_limit can refuse to enlarge or to shrink. max_megapixels lowers the size to a cap.
4. Optional: connect a mask so it is resized together with the picture.
5. The picture, the final width and height, the mask and an info line with the scale come out.
