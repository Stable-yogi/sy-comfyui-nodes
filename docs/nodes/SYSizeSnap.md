# Size Snap SY (`SYSizeSnap`)

Source: `nodes/sy_size_snap.py`

**What it does:** Snaps a width and height to a multiple, like 8 or 64, so a model accepts them. Pick nearest, round up or round down. The info line shows what changed and how much the shape moved. An optional megapixel cap stops a round-up from going over your memory.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width in pixels to snap. | 1 to 65536, default 1000 |
| height | INT | yes | Height in pixels to snap. | 1 to 65536, default 1000 |
| multiple | INT | yes | Snap to a multiple of this number. | 1 to 1024, default 8 |
| mode | COMBO | yes | Nearest rounds either way. Up never shrinks. Down never grows. | one of: nearest, up, down |
| max_megapixels | FLOAT | no | 0 is off. Example: 2.0 makes sure the snapped size stays under 2 million pixels. | 0.0 to 4096.0, step 0.1, default 0.0 |

Outputs: `INT`, `INT`, `STRING`

## How to use

1. Type the width and height, or connect them.
2. Set multiple (for example 8 or 64) and mode: nearest, up (never shrinks) or down (never grows).
3. Optional: set max_megapixels (0 is off) so a round-up stays under your limit.
4. The snapped width and height come out. The info line shows what changed.
