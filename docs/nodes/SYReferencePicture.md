# Reference Picture SY (`SYReferencePicture`)

Source: `nodes/sy_reference_picture.py`

**What it does:** Loads one reference picture and names it for your prompt (Image 1, Image 2 ...). An on/off switch turns the slot off without bypassing, and a size limit saves memory.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | COMBO | yes | The picture file in the ComfyUI input folder. You can also upload one. | one of: example.png, (none) |
| enabled | BOOLEAN | yes | Off: this slot gives a blank picture and active = false. | default True |
| slot | INT | yes | The number used in the label: Image 1, Image 2 and so on. | 1 to 99, default 1 |
| description | STRING | yes | A few words about the picture, e.g. the hero. Goes into the label. | default '' |
| max_side | INT | yes | Longest side in pixels. 0 keeps the original size. | 0 to 16384, default 0 |

Outputs: `IMAGE`, `MASK`, `INT`, `INT`, `BOOLEAN`, `STRING`

## How to use

1. Pick a picture in image (or upload one) and set slot to its number: Image 1, Image 2 and so on.
2. Write a few words in description. They go into the label.
3. Set max_side to limit the longest side and save memory. 0 keeps the original size.
4. Turn enabled off to switch the slot off without bypassing. It then gives a blank picture and active = false.
Outputs: image, mask, width, height, active and label.
