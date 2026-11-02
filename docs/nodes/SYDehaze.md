# Dehaze SY (`SYDehaze`)

Source: `nodes/sy_dehaze.py`

**What it does:** Removes haze or fog by stretching contrast and colour in the hazy areas. Sky protection keeps a very bright sky from turning dark or blue. Amount 0 does nothing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The hazy picture or pictures. | picture batch [B,H,W,3] |
| amount | FLOAT | yes | How much haze to remove. 0 does nothing. | 0.0 to 1.0, step 0.01, default 0.5 |
| patch | INT | yes | Size of the area used to find haze, an odd number. Bigger is smoother. | 3 to 61, step 2, default 15 |
| sky_protect | FLOAT | yes | Keeps very bright sky from going dark or blue. | 0.0 to 1.0, step 0.01, default 0.5 |
| saturation_back | FLOAT | yes | Adds colour back after the haze is gone. | 0.0 to 1.0, step 0.01, default 0.3 |

Outputs: `IMAGE`

## How to use

1. Connect a picture or batch to **image**.
2. Raise **amount** until the haze is gone but the picture still looks natural.
3. Use a bigger **patch** (odd numbers only) for smoother results, a smaller one for finer detail.
4. Raise **sky_protect** if a bright sky goes dark or blue.
5. Use **saturation_back** to bring colour back.
6. The output **IMAGE** has the same size; an alpha channel is passed through.

Notes: the haze map is worked out on a copy of at most 768 pixels on the long side, then scaled back up, so big pictures stay fast.
