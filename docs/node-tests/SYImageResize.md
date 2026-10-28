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

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 2 | width = 1 (min) | PASS | IMAGE=tensor[1, 1024, 8, 3]; INT=int 8; INT=int 1024 |
| 3 | width = 16384 (max) | PASS | IMAGE=tensor[1, 1024, 16384, 3]; INT=int 16384; INT=int 1024 |
| 4 | width = 8192 (mid) | PASS | IMAGE=tensor[1, 1024, 8192, 3]; INT=int 8192; INT=int 1024 |
| 5 | height = 1 (min) | PASS | IMAGE=tensor[1, 8, 1024, 3]; INT=int 1024; INT=int 8 |
| 6 | height = 16384 (max) | PASS | IMAGE=tensor[1, 16384, 1024, 3]; INT=int 1024; INT=int 16384 |
| 7 | height = 8192 (mid) | PASS | IMAGE=tensor[1, 8192, 1024, 3]; INT=int 1024; INT=int 8192 |
| 8 | mode = 'fit inside' | PASS | IMAGE=tensor[1, 680, 1024, 3]; INT=int 1024; INT=int 680 |
| 9 | mode = 'fill and crop' | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 10 | mode = 'pad' | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 11 | multiple_of = 1 (min) | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 12 | multiple_of = 512 (max) | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 13 | multiple_of = 256 (mid) | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 14 | interpolation = 'bicubic' | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 15 | interpolation = 'area' | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 16 | interpolation = 'nearest-exact' | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 17 | pad_color = 'white' | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 18 | pad_color = 'grey' | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 19 | pad_color = 'red' | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 20 | pad_color = 'green' | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 21 | pad_color = 'blue' | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |
| 22 | custom_color = '' (empty) | PASS | IMAGE=tensor[1, 1024, 1024, 3]; INT=int 1024; INT=int 1024 |

## Verdict

All 22 cases behaved as expected (22 passed, 0 rejected with a clear message).
