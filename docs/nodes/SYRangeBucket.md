# Range Bucket SY (`SYRangeBucket`)

Source: `nodes/sy_range_bucket.py`

**What it does:** Turns a number into a label by which range it falls in, for example a frame count into short, medium or long. Give the edges and one label per range.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | FLOAT | yes | The number to sort into a range. | -1000000000000000.0 to 1000000000000000.0, step 0.01, default 0.0 |
| edges | STRING | yes | Where the ranges split: numbers going up, separated by commas. | default '48, 120' |
| labels | STRING | yes | One label per line. Needs one more line than there are edges. | default 'short\nmedium\nlong', multiline |
| inclusive | COMBO | yes | Which range a number exactly on an edge belongs to. | one of: lower edge in next range, upper edge in lower range |

Outputs: `STRING`, `INT`

## How to use

1. Connect or type the number in **value**.
2. Type the split points in **edges**, going up and separated by commas, for example 48, 120.
3. Type **labels**, one per line, with one more line than there are edges.
4. Pick **inclusive** to choose which range a number exactly on an edge belongs to.
5. The outputs give the **label** and its **index** (0 for the first range).
