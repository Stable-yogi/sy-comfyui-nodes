# Value Noise Image SY (`SYValueNoiseImage`)

Source: `nodes/sy_value_noise_image.py`

**What it does:** Makes a cloud, paper or grain texture from scratch with smooth seeded noise. Handy as an overlay or a mask source. The same seed gives the same picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width of the new picture in pixels. | 16 to 4096, step 1, default 512 |
| height | INT | yes | Height of the new picture in pixels. | 16 to 4096, step 1, default 512 |
| scale | FLOAT | yes | Size of the biggest blobs in pixels. Small gives fine grain, big gives clouds. | 2.0 to 256.0, step 1.0, default 48.0 |
| octaves | INT | yes | Layers of detail. Each layer has half the size and half the strength. | 1 to 6, step 1, default 4 |
| seed | INT | yes | Same seed gives the same picture. Change it for a new pattern. | 0 to 9007199254740991, default 0 |
| colour_a | STRING | yes | Colour of the darkest noise value, 3 or 6 hex digits like a web colour. | default '#000000' |
| colour_b | STRING | yes | Colour of the brightest noise value, 3 or 6 hex digits like a web colour. | default '#ffffff' |
| batch | INT | yes | How many pictures to make. Each one uses the next seed. | 1 to 64, step 1, default 1 |

Outputs: `IMAGE`, `MASK`

## How to use

1. Set **width** and **height** of the new picture; no input picture is needed.
2. Set **scale**: small gives fine grain, big gives clouds. Raise **octaves** for more layers of detail.
3. Type **colour_a** (darkest) and **colour_b** (brightest) as web colours, for example #000000 and #ffffff.
4. Set **seed**; the same seed gives the same picture. Set **batch** above 1 to make several, each with the next seed.
5. The outputs give the coloured **image** and the same noise as a **mask**.
