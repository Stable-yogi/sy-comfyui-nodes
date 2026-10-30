# Aspect From Size SY (`SYAspectFromSize`)

Source: `nodes/sy_aspect_from_image.py`

**What it does:** Reads a width and height and gives the ratio as text, like 16:9, plus the ratio as a number. An odd ratio is matched to the nearest common one.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Picture width in pixels. Used with height to find the shape, like 16:9. | 1 to 65536, default 1024 |
| height | INT | yes | Picture height in pixels. Used with width to find the shape, like 16:9. | 1 to 65536, default 1024 |

Outputs: `STRING`, `FLOAT`
