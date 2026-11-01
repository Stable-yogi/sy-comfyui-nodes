# Unbundle SY (`SYUnbundle`)

Source: `nodes/sy_bundle.py`

**What it does:** Opens a bundle made by Bundle SY and gives every item its own output. An item that is not in the bundle does not crash anything: pictures, models and similar come out empty (None), numbers come out as 0, and texts come out empty. The last output, missing, lists the names that were not in the bundle, so you can see what to plug into Bundle SY.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| bundle | SY_BUNDLE | yes | The bundle to open. It comes from Bundle SY. |  |

Outputs: `SY_BUNDLE`, `MODEL`, `CLIP`, `VAE`, `CONDITIONING`, `CONDITIONING`, `LATENT`, `IMAGE`, `MASK`, `INT`, `INT`, `FLOAT`, `FLOAT`, `INT`, `INT`, `STRING`, `STRING`, `STRING`, `STRING`, `*`, `STRING`, `STRING`

## How to use

1. Connect the bundle from Bundle SY to bundle.
2. Every item in the bundle comes out on its own output.
3. An item that is not in the bundle gives None for pictures and models, 0 for numbers and empty text for texts.
4. The missing output lists the names that were not in the bundle.
