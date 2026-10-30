# Ping Pong SY (`SYPingPong`)

Source: `nodes/sy_ping_pong.py`

**What it does:** Adds the frames played backwards after the forward ones, so a clip goes there and back and loops smoothly.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames to play forward and then backward. | picture batch [B,H,W,3] |
| repeat_ends | BOOLEAN | yes | On: show the first and last frame twice. Off: no doubled frames, best for loops. | default False |

Outputs: `IMAGE`, `INT`
