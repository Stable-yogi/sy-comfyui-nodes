# Fade Mask Batch SY (`SYFadeMaskBatch`)

Source: `nodes/sy_fade_mask_batch.py`

**What it does:** Makes a batch of masks that fade from one value to another. Direction whole fades the entire mask evenly. The other directions sweep a soft edge across the frame over time. Good for wipes and reveals.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Mask width in pixels. | 1 to 16384, default 512 |
| height | INT | yes | Mask height in pixels. | 1 to 16384, default 512 |
| frames | INT | yes | How many masks to make. | 1 to 4096, default 16 |
| start_value | FLOAT | yes | Mask value in the first frame (0 black, 1 white). | 0.0 to 1.0, step 0.01, default 0.0 |
| end_value | FLOAT | yes | Mask value in the last frame (0 black, 1 white). | 0.0 to 1.0, step 0.01, default 1.0 |
| curve | COMBO | yes | How the fade speeds up or slows down over time. | one of: linear, ease_in, ease_out, ease_in_out |
| direction | COMBO | yes | whole fades evenly; the others sweep a soft edge across the frame. | one of: whole, left_to_right, right_to_left, top_to_bottom, bottom_to_top |

Outputs: `MASK`, `STRING`

## How to use

1. Set **width**, **height** and **frames** to match your clip.
2. Pick **direction**: whole fades the whole mask evenly, the others sweep a soft edge across the picture (a wipe).
3. Set **start_value** and **end_value** (0 black, 1 white) and a **curve** for the speed.
4. Connect the **MASK** output to any node that takes a mask batch, to fade an effect in or out over time.
