# Frame Number Overlay SY (`SYFrameNumberOverlay`)

Source: `nodes/sy_frame_number_overlay.py`

**What it does:** Burns the frame number, and optionally the time, into a corner of every frame. Useful for checking cuts and timing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The clip as a batch of frames. | picture batch [B,H,W,3] |
| fps | FLOAT | yes | Frames per second, used to work out the time. | 1.0 to 240.0, step 0.5, default 24.0 |
| start_number | INT | yes | The number shown on the first frame. | 0 to 100000, default 0 |
| show | COMBO | yes | What to print: the frame number, the time, or both. | one of: frame, time, frame and time |
| corner | COMBO | yes | Which corner of the picture holds the label. | one of: top left, top right, bottom left, bottom right |
| size | INT | yes | Text height in pixels. | 8 to 200, default 28 |
| text_colour | STRING | yes | Text colour, as 3 or 6 hex digits like a web colour. | default '#ffffff' |
| box_colour | STRING | yes | Colour of the box behind the text, as hex digits. | default '#000000' |

Outputs: `IMAGE`

## How to use

1. Connect a clip (a batch of frames) to **images**.
2. Set **fps** to the speed of the clip, for example 24, so the time is right.
3. Set **start_number** to the number shown on the first frame (0 by default) and pick what to print in **show**: frame, time, or frame and time.
4. Choose **corner**, for example bottom right, and the text height in **size**, for example 28.
5. Set **text_colour** and **box_colour** (the box behind the text) so the label is easy to read.
