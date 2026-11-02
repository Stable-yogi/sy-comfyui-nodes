# Strobe Flash SY (`SYStrobeFlash`)

Source: `nodes/sy_strobe_flash.py`

**What it does:** Flashes the clip to white, black, a colour, or inverted colours on a steady beat. Each flash then fades back over a few frames. Frames are processed one at a time.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| every_n_frames | INT | yes | A new flash starts every this many frames. | 1 to 1000, default 12 |
| flash_frames | INT | yes | How many frames each flash stays at full strength. | 1 to 100, default 1 |
| mode | COMBO | yes | Flash to white, to black, to the colour below, or to inverted colours. | one of: white, black, invert, colour |
| strength | FLOAT | yes | How far the picture goes towards the flash. 1 is complete. | 0.0 to 1.0, step 0.01, default 0.8 |
| fade_out_frames | INT | yes | The flash fades back to the normal picture over this many frames. | 0 to 100, default 3 |
| colour_r | FLOAT | yes | Red part of the flash colour. Used only by mode colour. | 0.0 to 1.0, step 0.01, default 1.0 |
| colour_g | FLOAT | yes | Green part of the flash colour. Used only by mode colour. | 0.0 to 1.0, step 0.01, default 0.5 |
| colour_b | FLOAT | yes | Blue part of the flash colour. Used only by mode colour. | 0.0 to 1.0, step 0.01, default 0.0 |
| offset | INT | yes | The frame where the first flash happens. 0 is the first frame. | 0 to 1000, default 0 |

Outputs: `IMAGE`

## How to use

1. Connect the clip's frames, in order, to **images**.
2. Set **every_n_frames** for the beat and **flash_frames** for how long each flash lasts.
3. Pick the **mode**. For colour, set **colour_r**, **colour_g** and **colour_b**.
4. Use **strength** for how strong the flash is and **fade_out_frames** for how quickly it dies away.
5. Use **offset** to move the first flash later. The alpha channel, if there is one, is left alone.
