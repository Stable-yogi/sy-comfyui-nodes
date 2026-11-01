# Ping Pong SY (`SYPingPong`)

Source: `nodes/sy_ping_pong.py`

**What it does:** Adds the frames played backwards after the forward ones, so a clip goes there and back and loops smoothly. The info output tells how many frames came out.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames to play forward and then backward. | picture batch [B,H,W,3] |
| repeat_ends | BOOLEAN | yes | On: show the first and last frame twice. Off: no doubled frames, best for loops. | default False |

Outputs: `IMAGE`, `INT`, `STRING`

## How to use

1. Connect your frames to images.
2. The output plays them forward and then backward, so a clip goes there and back and loops smoothly.
3. repeat_ends on shows the first and last frame twice. Leave it off for loops.
Outputs: the frames, the frame count and an info line.
