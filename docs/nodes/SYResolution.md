# Resolution SY (`SYResolution`)

Source: `nodes/sy_resolution.py`

**What it does:** Picks a width and height for a model. Choose a model preset and an aspect ratio. Custom uses the megapixels and multiple you set.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model_preset | COMBO | yes | Picks the size the chosen model works best at. | one of: Krea 2 (1 MP), Qwen Image 2.1 (1.5 MP), MOSS-Image (multiple of 32), Flux (1 MP), Custom |
| aspect | COMBO | yes | The shape of the picture. 1:1 is square, 16:9 is wide screen. | one of: 1:1, 4:3, 3:2, 16:9, 21:9, 3:4, 2:3, 9:16 |
| orientation | COMBO | yes | Landscape is wider than tall. Portrait is taller than wide. | one of: landscape, portrait |
| megapixels | FLOAT | yes | Picture size in millions of pixels. 1.0 is about 1024 by 1024. | 0.1 to 16.0, step 0.05, default 1.0 |
| multiple | INT | yes | Width and height are rounded to a multiple of this. 16 suits most models. | 8 to 64, step 8, default 16 |

Outputs: `INT`, `INT`
