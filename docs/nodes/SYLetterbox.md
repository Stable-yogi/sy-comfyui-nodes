# Letterbox SY (`SYLetterbox`)

Source: `nodes/sy_letterbox.py`

**What it does:** Puts bars (any colour) around a picture so it fits a wanted shape such as 2.39:1 cinema, or crops it to that shape. The picture is never stretched.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or pictures to reshape. | picture batch [B,H,W,3] |
| aspect | STRING | yes | The wanted shape, width to height, like 2.39:1, 16:9, 1.85:1 or 1:1. | default '2.39:1' |
| bar_colour | STRING | yes | Colour of the bars as a web colour, like #000 or #111. | default '#000' |
| mode | COMBO | yes | Add bars keeps everything and grows the canvas. Crop to fit cuts the picture. | one of: add bars, crop to fit |

Outputs: `IMAGE`, `STRING`

## How to use

1. Connect a picture or a batch to **image**.
2. Type the wanted shape in **aspect**, for example 2.39:1 or 16:9.
3. Pick **mode**: add bars keeps the whole picture and grows the canvas, crop to fit cuts the picture to the shape.
4. If you add bars, type their colour in **bar_colour**, for example #000.
5. The second output **info** is a short text note about the result.
