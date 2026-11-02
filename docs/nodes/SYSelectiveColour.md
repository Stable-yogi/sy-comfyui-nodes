# Selective Colour SY (`SYSelectiveColour`)

Source: `nodes/sy_selective_colour.py`

**What it does:** Changes only one range of colours, for example just the greens or just the blues. Pick the colour with hue_centre, then shift it, make it stronger or weaker, or brighter or darker.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to change. | picture batch [B,H,W,3] |
| hue_centre | FLOAT | yes | The colour to change, as degrees on the colour wheel. 0 red, 120 green, 240 blue. | 0.0 to 360.0, step 1.0, default 120.0 |
| hue_width | FLOAT | yes | How wide a range of colours around the centre is changed, in degrees. | 5.0 to 180.0, step 1.0, default 40.0 |
| softness | FLOAT | yes | 0 gives a hard edge to the range. 1 fades it out smoothly. | 0.0 to 1.0, step 0.01, default 0.5 |
| hue_shift | FLOAT | yes | Turns the chosen colours round the colour wheel, in degrees. | -180.0 to 180.0, step 1.0, default 0.0 |
| saturation | FLOAT | yes | Makes the chosen colours stronger (above 0) or weaker (below 0). | -1.0 to 1.0, step 0.01, default 0.0 |
| brightness | FLOAT | yes | Makes the chosen colours brighter (above 0) or darker (below 0). | -1.0 to 1.0, step 0.01, default 0.0 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Set **hue_centre** to the colour you want to change and **hue_width** to how wide a range it covers.
3. Raise **softness** so the change fades out at the edge of the range.
4. Move **hue_shift**, **saturation** or **brightness** to change only those colours.
5. The output **IMAGE** has the same size; an alpha channel is passed through.
