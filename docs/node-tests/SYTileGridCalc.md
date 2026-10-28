# Tile Grid Calc SY (`SYTileGridCalc`)

Source: `nodes/sy_tile_grid_calc.py`

**What it does:** Counts the tiles needed to cover a picture for a tile size and overlap. Gives columns, rows, the total and a text line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Picture width in pixels. | 1 to 1000000, default 2048 |
| height | INT | yes | Picture height in pixels. | 1 to 1000000, default 2048 |
| tile_size | INT | yes | Width and height of one square tile in pixels. | 1 to 1000000, default 1024 |
| overlap | INT | yes | Pixels shared by neighbour tiles. Must be less than the tile size. | 0 to 1000000, default 64 |

Outputs: `INT`, `INT`, `INT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 3; INT=int 3; INT=int 9; STRING=str '2048x2048 picture, tile 1024, overlap 64: 3 columns x 3 rows = 9 tiles' |
| 2 | width = 1 (min) | PASS | INT=int 1; INT=int 3; INT=int 3; STRING=str '1x2048 picture, tile 1024, overlap 64: 1 columns x 3 rows = 3 tiles' |
| 3 | width = 1000000 (max) | PASS | INT=int 1042; INT=int 3; INT=int 3126; STRING=str '1000000x2048 picture, tile 1024, overlap 64: 1042 columns x 3 rows = 3126 tiles' |
| 4 | width = 500000 (mid) | PASS | INT=int 521; INT=int 3; INT=int 1563; STRING=str '500000x2048 picture, tile 1024, overlap 64: 521 columns x 3 rows = 1563 tiles' |
| 5 | height = 1 (min) | PASS | INT=int 3; INT=int 1; INT=int 3; STRING=str '2048x1 picture, tile 1024, overlap 64: 3 columns x 1 rows = 3 tiles' |
| 6 | height = 1000000 (max) | PASS | INT=int 3; INT=int 1042; INT=int 3126; STRING=str '2048x1000000 picture, tile 1024, overlap 64: 3 columns x 1042 rows = 3126 tiles' |
| 7 | height = 500000 (mid) | PASS | INT=int 3; INT=int 521; INT=int 1563; STRING=str '2048x500000 picture, tile 1024, overlap 64: 3 columns x 521 rows = 1563 tiles' |
| 8 | tile_size = 1 (min) | REJECTED | ValueError: overlap (64) must be smaller than tile_size (1) |
| 9 | tile_size = 1000000 (max) | PASS | INT=int 1; INT=int 1; INT=int 1; STRING=str '2048x2048 picture, tile 1000000, overlap 64: 1 columns x 1 rows = 1 tiles' |
| 10 | tile_size = 500000 (mid) | PASS | INT=int 1; INT=int 1; INT=int 1; STRING=str '2048x2048 picture, tile 500000, overlap 64: 1 columns x 1 rows = 1 tiles' |
| 11 | overlap = 0 (min) | PASS | INT=int 2; INT=int 2; INT=int 4; STRING=str '2048x2048 picture, tile 1024, overlap 0: 2 columns x 2 rows = 4 tiles' |
| 12 | overlap = 1000000 (max) | REJECTED | ValueError: overlap (1000000) must be smaller than tile_size (1024) |
| 13 | overlap = 500000 (mid) | REJECTED | ValueError: overlap (500000) must be smaller than tile_size (1024) |

## Verdict

All 13 cases behaved as expected (10 passed, 3 rejected with a clear message).
