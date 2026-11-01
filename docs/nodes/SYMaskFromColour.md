# MaskFromColour SY (`SYMaskFromColour`)

Source: `nodes/sy_mask_from_colour.py`

**What it does:** Makes a mask from every pixel close to a chosen colour (type numbers or paste a hex colour). Tolerance sets how close. The info output says how much matched, and warns when nothing did.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture to pick the colour from. | picture batch [B,H,W,3] |
| red | INT | yes | Red part of the wanted colour, 0 to 255. | 0 to 255, step 1, default 0 |
| green | INT | yes | Green part of the wanted colour, 0 to 255. | 0 to 255, step 1, default 255 |
| blue | INT | yes | Blue part of the wanted colour, 0 to 255. | 0 to 255, step 1, default 0 |
| tolerance | INT | yes | How far each colour part may differ and still count. 0 is an exact match. | 0 to 255, step 1, default 20 |
| hex_colour | STRING | no | Optional web colour such as ff8800 or #f80. When filled it replaces red, green and blue. | default '' |
| invert | BOOLEAN | no | On: white becomes everything that does NOT match the colour. | default False |

Outputs: `MASK`, `STRING`

## How to use

1. Connect your picture to image.
2. Give the wanted colour as red, green and blue (0 to 255), or type a web colour such as ff8800 in hex_colour. A filled hex_colour replaces the three numbers.
3. Set tolerance. 0 matches the exact colour only. Higher values accept near colours.
4. Turn invert on to select everything that does not match.
The info output says how much matched and warns when nothing did.
