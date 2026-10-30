# Checkerboard SY (`SYCheckerboard`)

Source: `nodes/sy_checkerboard.py`

**What it does:** Makes a new picture of two alternating colour squares, handy as a test pattern or background.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width of the new picture in pixels. | 1 to 8192, step 1, default 1024 |
| height | INT | yes | Height of the new picture in pixels. | 1 to 8192, step 1, default 1024 |
| cell | INT | yes | Side length of one square in pixels. | 1 to 2048, step 1, default 64 |
| colour_a | STRING | yes | Colour of the first square, 3 or 6 hex digits like a web colour. | default '#808080' |
| colour_b | STRING | yes | Colour of the other squares, 3 or 6 hex digits like a web colour. | default '#c0c0c0' |
| batch_size | INT | yes | How many identical pictures to make. | 1 to 64, step 1, default 1 |

Outputs: `IMAGE`
