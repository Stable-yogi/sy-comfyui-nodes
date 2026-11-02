# Colour Balance 3-Way SY (`SYColourBalance3Way`)

Source: `nodes/sy_colour_balance_3way.py`

**What it does:** Tints the dark parts, the middle and the bright parts of a picture separately. Push red, green or blue up or down in each zone. All sliders at 0 do nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to tint. | picture batch [B,H,W,3] |
| shadow_red | FLOAT | yes | Tint of the dark parts: red (up) or cyan (down). | -1.0 to 1.0, step 0.01, default 0.0 |
| shadow_green | FLOAT | yes | Tint of the dark parts: green (up) or magenta (down). | -1.0 to 1.0, step 0.01, default 0.0 |
| shadow_blue | FLOAT | yes | Tint of the dark parts: blue (up) or yellow (down). | -1.0 to 1.0, step 0.01, default 0.0 |
| mid_red | FLOAT | yes | Tint of the middle tones: red (up) or cyan (down). | -1.0 to 1.0, step 0.01, default 0.0 |
| mid_green | FLOAT | yes | Tint of the middle tones: green (up) or magenta (down). | -1.0 to 1.0, step 0.01, default 0.0 |
| mid_blue | FLOAT | yes | Tint of the middle tones: blue (up) or yellow (down). | -1.0 to 1.0, step 0.01, default 0.0 |
| high_red | FLOAT | yes | Tint of the bright parts: red (up) or cyan (down). | -1.0 to 1.0, step 0.01, default 0.0 |
| high_green | FLOAT | yes | Tint of the bright parts: green (up) or magenta (down). | -1.0 to 1.0, step 0.01, default 0.0 |
| high_blue | FLOAT | yes | Tint of the bright parts: blue (up) or yellow (down). | -1.0 to 1.0, step 0.01, default 0.0 |
| strength | FLOAT | yes | How much of the tint is used. 0 gives the original picture. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Pick a zone (shadow, mid or high) and move its red, green and blue sliders.
3. Use **strength** to fade the whole effect in or out.
4. The output **IMAGE** has the same size; an alpha channel is passed through.
