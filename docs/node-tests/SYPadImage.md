# Pad Image SY (`SYPadImage`)

Source: `nodes/sy_pad_image.py`

**What it does:** Adds space around a picture. Also gives a mask that is white on the new space, ready for outpainting.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to add space around. | picture batch [B,H,W,3] |
| left | INT | yes | Pixels to add on the left. | 0 to 8192, default 0 |
| right | INT | yes | Pixels to add on the right. | 0 to 8192, default 0 |
| top | INT | yes | Pixels to add on the top. | 0 to 8192, default 0 |
| bottom | INT | yes | Pixels to add at the bottom. | 0 to 8192, default 0 |
| color | COMBO | yes | Colour that fills the new space. | one of: black, white, grey, red, green, blue |
| custom_color | STRING | no | Optional own colour as red,green,blue numbers 0 to 255, for example 200,120,40. Empty uses the list. | default '' |

Outputs: `IMAGE`, `MASK`, `INT`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; INT=int 96; INT=int 64 |
| 2 | left = 8192 (max) | PASS | IMAGE=tensor[1, 64, 8288, 3]; MASK=tensor[1, 64, 8288]; INT=int 8288; INT=int 64 |
| 3 | left = 4096 (mid) | PASS | IMAGE=tensor[1, 64, 4192, 3]; MASK=tensor[1, 64, 4192]; INT=int 4192; INT=int 64 |
| 4 | right = 8192 (max) | PASS | IMAGE=tensor[1, 64, 8288, 3]; MASK=tensor[1, 64, 8288]; INT=int 8288; INT=int 64 |
| 5 | right = 4096 (mid) | PASS | IMAGE=tensor[1, 64, 4192, 3]; MASK=tensor[1, 64, 4192]; INT=int 4192; INT=int 64 |
| 6 | top = 8192 (max) | PASS | IMAGE=tensor[1, 8256, 96, 3]; MASK=tensor[1, 8256, 96]; INT=int 96; INT=int 8256 |
| 7 | top = 4096 (mid) | PASS | IMAGE=tensor[1, 4160, 96, 3]; MASK=tensor[1, 4160, 96]; INT=int 96; INT=int 4160 |
| 8 | bottom = 8192 (max) | PASS | IMAGE=tensor[1, 8256, 96, 3]; MASK=tensor[1, 8256, 96]; INT=int 96; INT=int 8256 |
| 9 | bottom = 4096 (mid) | PASS | IMAGE=tensor[1, 4160, 96, 3]; MASK=tensor[1, 4160, 96]; INT=int 96; INT=int 4160 |
| 10 | color = 'white' | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; INT=int 96; INT=int 64 |
| 11 | color = 'grey' | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; INT=int 96; INT=int 64 |
| 12 | color = 'red' | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; INT=int 96; INT=int 64 |
| 13 | color = 'green' | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; INT=int 96; INT=int 64 |
| 14 | color = 'blue' | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; INT=int 96; INT=int 64 |
| 15 | custom_color = '' (empty) | PASS | IMAGE=tensor[1, 64, 96, 3]; MASK=tensor[1, 64, 96]; INT=int 96; INT=int 64 |

## Verdict

All 15 cases behaved as expected (15 passed, 0 rejected with a clear message).
