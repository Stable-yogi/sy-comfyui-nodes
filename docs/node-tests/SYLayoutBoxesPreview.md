# Layout Boxes Preview SY (`SYLayoutBoxesPreview`)

Source: `nodes/sy_layout_boxes_preview.py`

**What it does:** Draws layout boxes and their labels over a picture, or over a blank canvas when no picture is connected.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| layout_boxes | STRING | yes | The box list as JSON text. Connect a Layout Box or Merge node, or paste it. | default '', multiline |
| line_width | INT | yes | Thickness of the box outline in pixels. | 1 to 32, default 3 |
| show_labels | BOOLEAN | yes | Write each box label above its top left corner. | default True |
| blank_width | INT | yes | Width of the blank canvas. Used only when no picture is connected. | 8 to 16384, default 1024 |
| blank_height | INT | yes | Height of the blank canvas. Used only when no picture is connected. | 8 to 16384, default 1024 |
| image | IMAGE | no | Optional picture to draw on. Leave it out to use a blank canvas. | picture batch [B,H,W,3] |

Outputs: `IMAGE`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 2 | layout_boxes = '' (empty) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 3 | line_width = 1 (min) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 4 | line_width = 32 (max) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 5 | line_width = 16 (mid) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 6 | show_labels = False | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 7 | blank_width = 8 (min) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 8 | blank_width = 16384 (max) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 9 | blank_width = 8196 (mid) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 10 | blank_height = 8 (min) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 11 | blank_height = 16384 (max) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |
| 12 | blank_height = 8196 (mid) | REJECTED | ValueError: the box text is empty; connect a Layout Box node or paste a JSON list |

## Verdict

All 12 cases behaved as expected (0 passed, 12 rejected with a clear message).
