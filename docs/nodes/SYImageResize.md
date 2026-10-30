# Image Resize SY (`SYImageResize`)

Source: `nodes/sy_image_resize.py`

**What it does:** Changes the size of a picture. Stretch, fit inside the box, fill the box and crop the extra, or pad the gaps with a colour.

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

Outputs: `IMAGE`, `INT`, `INT`
