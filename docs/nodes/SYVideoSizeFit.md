# Video Size Fit SY (`SYVideoSizeFit`)

Source: `nodes/sy_video_size_fit.py`

**What it does:** Gives a new width and height with the same shape that stays inside a pixel budget and is a multiple of a number.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Current width in pixels. | 1 to 16384, default 1280 |
| height | INT | yes | Current height in pixels. | 1 to 16384, default 720 |
| max_pixels | FLOAT | yes | Pixel budget in megapixels. The result never goes above it. | 0.001 to 1000.0, step 0.01, default 0.9 |
| multiple_of | INT | yes | Width and height are rounded to a multiple of this number. | 1 to 256, default 32 |

Outputs: `INT`, `INT`
