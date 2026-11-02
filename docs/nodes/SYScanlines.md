# Scanlines SY (`SYScanlines`)

Source: `nodes/sy_scanlines.py`

**What it does:** Gives a picture an old monitor look by darkening every few rows with a smooth profile. An optional wave makes the lines slightly curved.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch to add scanlines to. | picture batch [B,H,W,3] |
| line_gap | INT | yes | Distance in pixels from one dark line to the next. | 2 to 16, step 1, default 3 |
| darkness | FLOAT | yes | How dark the lines get. 0 leaves the picture unchanged. | 0.0 to 1.0, step 0.01, default 0.35 |
| wobble | FLOAT | yes | Waviness of the lines in pixels. 0 keeps them straight. | 0.0 to 4.0, step 0.1, default 0.0 |
| offset | INT | yes | Moves the lines down by this many pixels. | 0 to 15, step 1, default 0 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or a batch to **image**.
2. Set **line_gap** for the distance between dark lines.
3. Set **darkness**; 0 leaves the picture unchanged.
4. Add **wobble** to curve the lines slightly, and **offset** to move them down.
5. The output **IMAGE** is the picture with scanlines.
