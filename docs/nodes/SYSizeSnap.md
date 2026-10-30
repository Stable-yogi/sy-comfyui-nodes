# Size Snap SY (`SYSizeSnap`)

Source: `nodes/sy_size_snap.py`

**What it does:** Snaps a width and height to a multiple, like 8 or 64, so a model accepts them. Pick nearest, round up or round down.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width in pixels to snap. | 1 to 65536, default 1000 |
| height | INT | yes | Height in pixels to snap. | 1 to 65536, default 1000 |
| multiple | INT | yes | Snap to a multiple of this number. | 1 to 1024, default 8 |
| mode | COMBO | yes | Nearest rounds either way. Up never shrinks. Down never grows. | one of: nearest, up, down |

Outputs: `INT`, `INT`
