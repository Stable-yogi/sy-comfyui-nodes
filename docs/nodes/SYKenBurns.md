# Ken Burns SY (`SYKenBurns`)

Source: `nodes/sy_ken_burns.py`

**What it does:** Turns one picture into a slow zoom-and-pan clip. The output has the same size as the picture. Only the first picture of a batch is used.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to animate. If it is a batch, the first picture is used. | picture batch [B,H,W,3] |
| frames | INT | yes | How many frames the clip has. | 2 to 600, default 48 |
| zoom_start | FLOAT | yes | Zoom at the first frame. 1 shows the whole picture. | 1.0 to 4.0, step 0.01, default 1.0 |
| zoom_end | FLOAT | yes | Zoom at the last frame. Bigger means closer. | 1.0 to 4.0, step 0.01, default 1.3 |
| pan_x | FLOAT | yes | Sideways move. The view goes from minus this to plus this of the free space. | -1.0 to 1.0, step 0.05, default 0.0 |
| pan_y | FLOAT | yes | Up and down move. Works like pan_x. Minus starts at the top. | -1.0 to 1.0, step 0.05, default 0.0 |
| ease | COMBO | yes | Linear moves at a steady pace. Ease in out starts and ends gently. | one of: linear, ease in out |

Outputs: `IMAGE`

## How to use

1. Connect one picture to **image**. If you give a batch, only the first picture is used.
2. Set **frames** to the length of the clip, for example 48.
3. Set **zoom_start** to 1.0 (whole picture) and **zoom_end** to 1.3 for a slow move closer.
4. Use **pan_x** and **pan_y** to slide the view, for example 0.5 for **pan_x**. Leave them at 0 for a straight zoom.
5. Pick **ease**: linear for a steady move, or ease in out for a gentle start and end.
