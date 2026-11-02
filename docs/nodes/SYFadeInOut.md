# Fade In Out SY (`SYFadeInOut`)

Source: `nodes/sy_fade_in_out.py`

**What it does:** Fades a clip in from a colour and out to a colour, such as black or white. If the two fades are longer than the clip they are shortened to fit. Transparency is left alone.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The clip as a batch of frames. | picture batch [B,H,W,3] |
| fade_in | INT | yes | Frames at the start that fade in from the colour. 0 means none. | 0 to 300, default 12 |
| fade_out | INT | yes | Frames at the end that fade out to the colour. 0 means none. | 0 to 300, default 12 |
| colour | STRING | yes | Fade colour, as 3 or 6 hex digits like a web colour. | default '#000000' |
| curve | COMBO | yes | Linear fades at a steady pace. Ease in out starts and ends gently. | one of: linear, ease in out |

Outputs: `IMAGE`

## How to use

1. Connect a clip (a batch of frames) to **images**.
2. Set **fade_in** and **fade_out** to the number of frames to fade at the start and end, for example 12 each. 0 means no fade on that side.
3. Type the fade colour in **colour**, for example #000000 for black or #ffffff for white.
4. Pick **curve**: linear for a steady fade, or ease in out for a gentle start and end.
