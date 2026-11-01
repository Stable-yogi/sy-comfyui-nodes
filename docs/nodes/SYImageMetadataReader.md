# Image Metadata Reader SY (`SYImageMetadataReader`)

Source: `nodes/sy_image_metadata_reader.py`

**What it does:** Reads the prompt and workflow text saved inside a png file from the input folder. It never changes the file. Optional source can look in the output folder instead. Also splits out the positive and negative prompt and the main settings (seed, steps, cfg, model), reads Forge/A1111 'parameters' text, and says what was found.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| file | STRING | yes | A .png file inside the input folder, like image.png or a/b.png. | default '' |
| source | COMBO | no | Which ComfyUI folder the file is in. | one of: input, output |

Outputs: `STRING`, `STRING`, `STRING`, `STRING`, `STRING`, `STRING`, `STRING`

## How to use

1. Type file, a .png in the input folder, like image.png or a/b.png. Set source to output to look in the output folder instead.
2. The node reads the prompt and workflow text saved inside the png. It never changes the file.
3. It splits out the positive and negative prompt and the main settings (seed, steps, cfg, model), and also reads Forge style parameters text. An info line says what was found.
