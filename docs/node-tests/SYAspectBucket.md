# Aspect Bucket SY (`SYAspectBucket`)

Source: `nodes/sy_aspect_bucket.py`

**What it does:** Picks the training size whose shape is closest to your picture, for example 1344x768 for a wide picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width of your picture in pixels. | 1 to 65536, default 1024 |
| height | INT | yes | Height of your picture in pixels. | 1 to 65536, default 1024 |
| buckets | STRING | yes | Allowed shapes as ratios, separated by commas, for example 1:1, 4:3, 16:9. | default '1:1, 4:3, 3:2, 16:9' |
| include_flips | BOOLEAN | yes | On: also allow the upright version of each shape, so 4:3 gives 3:4 too. | default True |
| target_resolution | INT | yes | Side of the square the bucket area is based on. 1024 gives about one megapixel. | 64 to 8192, default 1024 |
| multiple_of | INT | yes | Bucket width and height are rounded to a multiple of this number. | 1 to 512, default 64 |

Outputs: `INT`, `INT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 1024; INT=int 1024; STRING=str '1:1' |
| 2 | width = 1 (min) | PASS | INT=int 768; INT=int 1344; STRING=str '9:16' |
| 3 | width = 65536 (max) | PASS | INT=int 1344; INT=int 768; STRING=str '16:9' |
| 4 | width = 32768 (mid) | PASS | INT=int 1344; INT=int 768; STRING=str '16:9' |
| 5 | height = 1 (min) | PASS | INT=int 1344; INT=int 768; STRING=str '16:9' |
| 6 | height = 65536 (max) | PASS | INT=int 768; INT=int 1344; STRING=str '9:16' |
| 7 | height = 32768 (mid) | PASS | INT=int 768; INT=int 1344; STRING=str '9:16' |
| 8 | buckets = '' (empty) | REJECTED | ValueError: the bucket list is empty; write ratios like 1:1, 4:3, 16:9 |
| 9 | include_flips = False | PASS | INT=int 1024; INT=int 1024; STRING=str '1:1' |
| 10 | target_resolution = 64 (min) | PASS | INT=int 64; INT=int 64; STRING=str '1:1' |
| 11 | target_resolution = 8192 (max) | PASS | INT=int 8192; INT=int 8192; STRING=str '1:1' |
| 12 | target_resolution = 4128 (mid) | PASS | INT=int 4160; INT=int 4160; STRING=str '1:1' |
| 13 | multiple_of = 1 (min) | PASS | INT=int 1024; INT=int 1024; STRING=str '1:1' |
| 14 | multiple_of = 512 (max) | PASS | INT=int 1024; INT=int 1024; STRING=str '1:1' |
| 15 | multiple_of = 256 (mid) | PASS | INT=int 1024; INT=int 1024; STRING=str '1:1' |

## Verdict

All 15 cases behaved as expected (14 passed, 1 rejected with a clear message).
