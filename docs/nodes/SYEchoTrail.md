# Echo Trail SY (`SYEchoTrail`)

Source: `nodes/sy_echo_trail.py`

**What it does:** Makes ghost trails. Each frame is mixed with the frames before it, and older frames fade out, so anything that moves leaves a trail behind it. A single picture comes back unchanged.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames of the clip, in order. | picture batch [B,H,W,3] |
| echoes | INT | yes | How many earlier frames are mixed into each frame. | 1 to 12, default 4 |
| decay | FLOAT | yes | How much each older frame counts compared with the one after it. 0 = no trail. | 0.0 to 1.0, step 0.01, default 0.6 |
| mode | COMBO | yes | Average blends the frames. Lighten keeps the brightest pixel, so bright things leave streaks. | one of: average, lighten |

Outputs: `IMAGE`

## How to use

1. Connect the clip's frames, in order, to **images**.
2. Set **echoes** to how many earlier frames are mixed into each frame.
3. Set **decay**: lower fades older frames faster, 0 gives no trail.
4. Pick **mode**: average blends the frames, lighten lets bright things leave streaks.
5. The output **IMAGE** is the clip with ghost trails. A single picture comes back unchanged.
