# Free VRAM SY (`SYFreeVRAM`)

Source: `nodes/sy_free_vram.py`

**What it does:** Passes any value through. When enabled, unloads models and clears the GPU memory cache so the next step has more room.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | * | yes | Anything you pass through. It comes out unchanged, after memory is freed. |  |
| enabled | BOOLEAN | yes | On: free graphics card memory when this runs. Off: do nothing. | default True |

Outputs: `*`, `STRING`
