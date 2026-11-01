# Frame Select SY (`SYFrameSelect`)

Source: `nodes/sy_frame_select.py`

**What it does:** Takes some frames from a batch: from start to end (both included), every step frames. Negative numbers count from the end. Turn on clamp to cope with a start or end past the batch instead of getting an error.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The batch of frames to take from. | picture batch [B,H,W,3] |
| start | INT | yes | First frame to keep, counting from 0. -1 means the last frame. | -100000 to 100000, default 0 |
| end | INT | yes | Last frame to keep, included. -1 means the last frame. | -100000 to 100000, default -1 |
| step | INT | yes | Keep every this many frames. 2 keeps every second frame. | 1 to 1000, default 1 |
| clamp | BOOLEAN | no | On: a start or end past the batch is moved to the first or last frame instead of an error. | default False |

Outputs: `IMAGE`, `INT`, `STRING`

## How to use

1. Connect your frames to images.
2. Set start and end (both included) and step. Negative numbers count from the end.
3. Turn on clamp to cope with a start or end past the batch instead of an error.
4. Outputs: images, count and info.
