# Aspect Bucket SY (`SYAspectBucket`)

Source: `nodes/sy_aspect_bucket.py`

**What it does:** Picks the training size whose shape is closest to your picture, for example 1344x768 for a wide picture.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| width | INT | yes | Width of your picture in pixels. | 1 to 65536, default 1024 |
| height | INT | yes | Height of your picture in pixels. | 1 to 65536, default 1024 |
| buckets | STRING | yes | Allowed shapes as ratios, separated by commas, for example 1:1, 4:3, 16:9. | default '1:1, 4:3, 3:2, 16:9' |
| include_flips | BOOLEAN | yes | On: also allow the upright version of each shape, so 4:3 gives 3:4 too. | default True |
| target_resolution | INT | yes | Side of the square the bucket area is based on. 1024 gives about one megapixel. | 64 to 8192, default 1024 |
| multiple_of | INT | yes | Bucket width and height are rounded to a multiple of this number. | 1 to 512, default 64 |

Outputs: `INT`, `INT`, `STRING`
