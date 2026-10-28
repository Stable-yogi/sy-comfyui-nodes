# Image Hash Duplicate Check SY (`SYImageHashDuplicate`)

Source: `nodes/sy_image_hash_duplicate.py`

**What it does:** Compares two pictures with a small fingerprint. Tells you how different they are and if they are near duplicates.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | First picture. If it is a batch, the first picture of the batch is used. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | Second picture. If it is a batch, the first picture of the batch is used. | picture batch [B,H,W,3] |
| hash_size | INT | yes | Fingerprint grid size. 8 gives 64 bits. Bigger notices smaller differences. | 4 to 32, default 8 |
| threshold | INT | yes | Largest number of differing bits that still counts as a near duplicate. | 0 to 1024, default 5 |

Outputs: `INT`, `BOOLEAN`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 0; BOOLEAN=bool True; STRING=str 'near duplicate: 0 of 64 hash bits differ (limit 5).' |
| 2 | hash_size = 4 (min) | PASS | INT=int 0; BOOLEAN=bool True; STRING=str 'near duplicate: 0 of 16 hash bits differ (limit 5).' |
| 3 | hash_size = 32 (max) | PASS | INT=int 0; BOOLEAN=bool True; STRING=str 'near duplicate: 0 of 1024 hash bits differ (limit 5).' |
| 4 | hash_size = 18 (mid) | PASS | INT=int 0; BOOLEAN=bool True; STRING=str 'near duplicate: 0 of 324 hash bits differ (limit 5).' |
| 5 | threshold = 0 (min) | PASS | INT=int 0; BOOLEAN=bool True; STRING=str 'near duplicate: 0 of 64 hash bits differ (limit 0).' |
| 6 | threshold = 1024 (max) | PASS | INT=int 0; BOOLEAN=bool True; STRING=str 'near duplicate: 0 of 64 hash bits differ (limit 1024).' |
| 7 | threshold = 512 (mid) | PASS | INT=int 0; BOOLEAN=bool True; STRING=str 'near duplicate: 0 of 64 hash bits differ (limit 512).' |

## Verdict

All 7 cases behaved as expected (7 passed, 0 rejected with a clear message).
