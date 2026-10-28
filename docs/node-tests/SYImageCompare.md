# Image Compare SY (`SYImageCompare`)

Source: `nodes/sy_image_compare.py`

**What it does:** Compares two pictures: side by side, difference, blend, checker or wipe. B is resized to match A.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a | IMAGE | yes | The first picture. Its size sets the result size. | picture batch [B,H,W,3] |
| image_b | IMAGE | yes | The second picture. It is resized to fit the first if needed. | picture batch [B,H,W,3] |
| mode | COMBO | yes | How to put the two pictures together. | one of: side_by_side, difference, blend, checker, wipe |
| amount | FLOAT | yes | Blend mix, or wipe position. 0 shows A, 1 shows B. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `IMAGE`

## How it was tested

This node was not run by the harness. Reason: skipped: touches disk (the code reads or writes files).


## Verdict

Not run. skipped: touches disk (the code reads or writes files).
