# Crossfade Slideshow SY (`SYCrossfadeSlideshow`)

Source: `nodes/sy_crossfade_slideshow.py`

**What it does:** Turns a batch of same-sized pictures into video frames. Every picture stays still for a while, then melts into the next one. Optionally melts from the last back to the first for a seamless loop.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The slides. Each picture in the batch is one slide. They must all be the same size. | picture batch [B,H,W,3] |
| hold_frames | INT | yes | How many frames each slide stays still. | 1 to 10000, default 24 |
| fade_frames | INT | yes | Frames of cross-fade between two slides. Not more than hold_frames. | 0 to 10000, default 12 |
| loop | BOOLEAN | yes | On: also fade from the last slide back to the first. | default False |
| ease | BOOLEAN | no | On: the fade starts and ends gently instead of at a steady speed. | default True |

Outputs: `IMAGE`, `INT`, `STRING`

## How to use

1. Load your pictures as one batch (for example with a folder loader). All must be the same size.
2. Connect the batch to **images**. Set **hold_frames** (how long each picture stays) and **fade_frames** (the melt between two pictures).
3. Turn **loop** on if the last picture should melt back into the first, for a clip that repeats.
4. Connect the **IMAGE** output to a video save node. The **INT** output is the frame count, the **STRING** says what was made.
