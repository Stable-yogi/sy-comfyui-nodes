# Layout Boxes Merge SY (`SYLayoutBoxesMerge`)

Source: `nodes/sy_layout_boxes_merge.py`

**What it does:** Joins up to eight box lists into one list, keeping the order. Empty inputs are skipped. Can drop exact copies, counts the boxes and warns when a label is used twice.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| boxes_1 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| boxes_2 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| boxes_3 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| boxes_4 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| boxes_5 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| boxes_6 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| boxes_7 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| boxes_8 | STRING | no | Box text from a Layout Box node or another merge. Leave empty to skip. | default '' |
| drop_duplicates | BOOLEAN | no | On removes a box that is an exact copy of an earlier one (same place, size, label, colour). | default False |

Outputs: `STRING`, `INT`, `STRING`
