# Glitch Slices SY (`SYGlitchSlices`)

Source: `nodes/sy_glitch_slices.py`

**What it does:** Digital glitch look. Random horizontal strips of the picture slide sideways, and the red and blue colours slide a little differently. The same seed gives the same glitch.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture (or batch of frames) to glitch. Each frame gets its own pattern. | picture batch [B,H,W,3] |
| slices | INT | yes | How many horizontal strips the picture is cut into. | 1 to 60, default 12 |
| max_shift | FLOAT | yes | Biggest sideways slide of a strip, as a share of the picture width. | 0.0 to 0.3, step 0.005, default 0.06 |
| channel_split | FLOAT | yes | How far red and blue slide apart, as a share of the picture width. | 0.0 to 0.05, step 0.001, default 0.01 |
| seed | INT | yes | Same seed gives the same glitch. Change it for a new pattern. | 0 to 9007199254740992, default 0 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or a batch of frames to **image**.
2. Set **slices** to the number of horizontal strips.
3. Set **max_shift** for how far strips slide sideways, and **channel_split** for how far red and blue drift apart.
4. Change **seed** for a new glitch pattern; the same seed repeats the same one.
5. The output **IMAGE** is the glitched picture.
