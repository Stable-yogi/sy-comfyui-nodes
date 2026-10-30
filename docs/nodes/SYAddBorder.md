# Add Border SY (`SYAddBorder`)

Source: `nodes/sy_add_border.py`

**What it does:** Adds a coloured border around a picture. Outside makes the picture bigger; inside paints over the edge. Also gives a mask of the border.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The picture or batch of pictures to put a border on. | picture batch [B,H,W,3] |
| size | INT | yes | Border thickness in pixels. 0 changes nothing. | 0 to 1024, step 1, default 16 |
| colour | STRING | yes | Border colour, as 3 or 6 hex digits like a web colour. | default '#000000' |
| mode | COMBO | yes | outside grows the picture; inside keeps the size and paints the edge. | one of: outside, inside |

Outputs: `IMAGE`, `MASK`
