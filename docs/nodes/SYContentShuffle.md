# ContentShuffle SY (`SYContentShuffle`)

Source: `nodes/sy_content_shuffle.py`

**What it does:** Keeps the colours and textures of a picture but scrambles where they are, by pushing every pixel along a smooth random wobble. Handy as a colour reference for control workflows. Same seed, same result.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture (or batch) to scramble. | picture batch [B,H,W,3] |
| seed | INT | yes | Picks the wobble pattern. The same seed gives the same result. | 0 to 4294967295, default 0 |
| strength | FLOAT | yes | How far pixels move. 0 changes nothing, 1 moves up to a quarter of the picture size. | 0.0 to 1.0, step 0.01, default 0.5 |
| scale | INT | yes | Wobble cells across the shorter side. A bigger number gives a finer wobble. | 2 to 64, default 8 |

Outputs: `IMAGE`

## How to use

1. Connect a picture to image.
2. Pick a seed. The same seed always gives the same result.
3. strength sets how far pixels move (0 changes nothing). scale sets how fine the wobble is.
Colours and textures stay, the places are scrambled. Use the result as a colour reference for control workflows.
Output: the scrambled picture.
