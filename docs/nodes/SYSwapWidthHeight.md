# Swap Width Height SY (`SYSwapWidthHeight`)

Source: `nodes/sy_swap_width_height.py`

**What it does:** Swaps width and height when the switch is on. Turns a landscape size into portrait and back.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width in pixels. | 0 to 65536, default 1024 |
| height | INT | yes | Height in pixels. | 0 to 65536, default 768 |
| swap | BOOLEAN | yes | On swaps the two sizes. Off passes them through unchanged. | default True |

Outputs: `INT`, `INT`
