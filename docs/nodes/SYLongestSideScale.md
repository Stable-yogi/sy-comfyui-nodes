# Longest Side Scale SY (`SYLongestSideScale`)

Source: `nodes/sy_longest_side_scale.py`

**What it does:** Works out a new width and height so the longer side equals the number you give. The shape (aspect) stays the same. Both sides are rounded to a multiple. Optional no_upscale and a megapixel cap keep small pictures small and big ones safe. The info line explains the result.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Current width in pixels. | 1 to 65536, default 1024 |
| height | INT | yes | Current height in pixels. | 1 to 65536, default 768 |
| longest_side | INT | yes | Size in pixels you want for the longer side. | 1 to 65536, default 1024 |
| multiple | INT | yes | Both sides are rounded to a multiple of this. Use 1 for exact. | 1 to 256, default 8 |
| no_upscale | BOOLEAN | no | On never makes the picture bigger than it is now. Small pictures keep their size. | default False |
| max_megapixels | FLOAT | no | 0 is off. Example: 2.0 keeps the result under 2 million pixels so it fits your card. | 0.0 to 4096.0, step 0.1, default 0.0 |

Outputs: `INT`, `INT`, `STRING`

## How to use

1. Type the current width and height and the longest_side you want.
2. The shape stays the same. Both sides are rounded to a multiple of multiple (use 1 for exact).
3. Optional: no_upscale keeps small pictures at their size, and max_megapixels (for example 2.0) caps the result so it fits your card. 0 is off.
4. The new width, the new height and an info line come out. Feed them to a resize node.
