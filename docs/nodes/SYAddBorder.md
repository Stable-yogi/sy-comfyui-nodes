# Add Border SY (`SYAddBorder`)

Source: `nodes/sy_add_border.py`

**What it does:** Adds a coloured border around a picture. Outside makes the picture bigger; inside paints over the edge. Also gives a mask of the border, and can round the new size up to a multiple of 8 or 64. Says what it did.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to put a border on. | picture batch [B,H,W,3] |
| size | INT | yes | Border thickness in pixels. 0 changes nothing. | 0 to 1024, step 1, default 16 |
| colour | STRING | yes | Border colour, as 3 or 6 hex digits like a web colour. | default '#000000' |
| mode | COMBO | yes | outside grows the picture; inside keeps the size and paints the edge. | one of: outside, inside |
| multiple_of | INT | no | Outside mode: round the new width and height up to this multiple, for example 8 or 64. 1 = off. | 1 to 512, step 1, default 1 |

Outputs: `IMAGE`, `MASK`, `STRING`

## How to use

1. Connect your picture to image.
2. Set size (thickness in pixels) and colour (a hex code such as #000000).
3. Pick mode: outside makes the picture bigger, inside keeps the size and paints over the edge.
4. Use multiple_of (8 or 64) if the next node needs a size that fits. The result comes out as image, with a mask of the border.
