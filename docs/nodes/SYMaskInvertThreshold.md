# MaskInvertThreshold SY (`SYMaskInvertThreshold`)

Source: `nodes/sy_mask_invert_threshold.py`

**What it does:** Flips a mask (white and black swap) and can first turn it into hard black and white at a cut-off value. The info output says what was done and how much is white, and warns about an all-black or all-white result.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mask | MASK | yes | The mask to change. | mask [B,H,W] |
| invert | BOOLEAN | yes | Swap white and black. | default True |
| use_threshold | BOOLEAN | yes | Turn soft grays into pure black or white first. | default False |
| threshold | FLOAT | yes | Values at or above this become white. Only used when use_threshold is on. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `MASK`, `STRING`

## How to use

1. Connect your mask.
2. Keep invert on to swap white and black.
3. Turn use_threshold on to make soft grays hard first. Values at or above threshold become white, the rest black.
The info output says what was done and warns about an all-black or all-white result.
