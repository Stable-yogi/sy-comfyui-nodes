# Video Size Presets SY (`SYVideoSizePresets`)

Source: `nodes/sy_video_size_presets.py`

**What it does:** Video sizes for models like Wan and LTX. Pick 480p, 720p or 1080p and a shape: wide 16:9, tall 9:16 or square 1:1. Both sides are rounded to 16 or 32.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| resolution | COMBO | yes | Length of the short side. 720p is 720 pixels. | one of: 480p, 720p, 1080p |
| aspect | COMBO | yes | 16:9 is wide, 9:16 is tall like a phone, 1:1 is square. | one of: 16:9, 9:16, 1:1 |
| multiple | COMBO | yes | Round both sides to this multiple. LTX style models like 32. | one of: 16, 32 |

Outputs: `INT`, `INT`
