# Image Metadata Reader SY (`SYImageMetadataReader`)

Source: `nodes/sy_image_metadata_reader.py`

**What it does:** Reads the prompt and workflow text saved inside a png file from the input folder. It never changes the file.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| file | STRING | yes | A .png file inside the input folder, like image.png or a/b.png. | default '' |

Outputs: `STRING`, `STRING`
