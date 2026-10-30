# Longest Side Scale SY (`SYLongestSideScale`)

Source: `nodes/sy_longest_side_scale.py`

**What it does:** Works out a new width and height so the longer side equals the number you give. The shape (aspect) stays the same. Both sides are rounded to a multiple.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Current width in pixels. | 1 to 65536, default 1024 |
| height | INT | yes | Current height in pixels. | 1 to 65536, default 768 |
| longest_side | INT | yes | Size in pixels you want for the longer side. | 1 to 65536, default 1024 |
| multiple | INT | yes | Both sides are rounded to a multiple of this. Use 1 for exact. | 1 to 256, default 8 |

Outputs: `INT`, `INT`
