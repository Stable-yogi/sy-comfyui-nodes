# Layout Box SY (`SYLayoutBox`)

Source: `nodes/sy_layout_box.py`

**What it does:** Makes one named box for a picture layout. Join several with Layout Boxes Merge, then check or preview them.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| x | INT | yes | Distance of the box left edge from the left of the picture, in pixels. | 0 to 16384, default 0 |
| y | INT | yes | Distance of the box top edge from the top of the picture, in pixels. | 0 to 16384, default 0 |
| w | INT | yes | Width of the box in pixels. | 1 to 16384, default 256 |
| h | INT | yes | Height of the box in pixels. | 1 to 16384, default 256 |
| label | STRING | yes | Short name shown on the box, up to 80 characters. | default 'box' |
| colour | COMBO | yes | Colour the preview uses to draw this box. | one of: red, orange, yellow, green, cyan, blue, purple, pink, white, black |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "red"}]' |
| 2 | x = 16384 (max) | PASS | STRING=str '[{"x": 16384, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "red"}]' |
| 3 | x = 8192 (mid) | PASS | STRING=str '[{"x": 8192, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "red"}]' |
| 4 | y = 16384 (max) | PASS | STRING=str '[{"x": 0, "y": 16384, "w": 256, "h": 256, "label": "box", "colour": "red"}]' |
| 5 | y = 8192 (mid) | PASS | STRING=str '[{"x": 0, "y": 8192, "w": 256, "h": 256, "label": "box", "colour": "red"}]' |
| 6 | w = 1 (min) | PASS | STRING=str '[{"x": 0, "y": 0, "w": 1, "h": 256, "label": "box", "colour": "red"}]' |
| 7 | w = 16384 (max) | PASS | STRING=str '[{"x": 0, "y": 0, "w": 16384, "h": 256, "label": "box", "colour": "red"}]' |
| 8 | w = 8192 (mid) | PASS | STRING=str '[{"x": 0, "y": 0, "w": 8192, "h": 256, "label": "box", "colour": "red"}]' |
| 9 | h = 1 (min) | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 1, "label": "box", "colour": "red"}]' |
| 10 | h = 16384 (max) | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 16384, "label": "box", "colour": "red"}]' |
| 11 | h = 8192 (mid) | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 8192, "label": "box", "colour": "red"}]' |
| 12 | label = '' (empty) | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "", "colour": "red"}]' |
| 13 | colour = 'orange' | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "orange"}]' |
| 14 | colour = 'yellow' | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "yellow"}]' |
| 15 | colour = 'green' | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "green"}]' |
| 16 | colour = 'cyan' | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "cyan"}]' |
| 17 | colour = 'blue' | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "blue"}]' |
| 18 | colour = 'purple' | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "purple"}]' |
| 19 | colour = 'pink' | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "pink"}]' |
| 20 | colour = 'white' | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "white"}]' |
| 21 | colour = 'black' | PASS | STRING=str '[{"x": 0, "y": 0, "w": 256, "h": 256, "label": "box", "colour": "black"}]' |

## Verdict

All 21 cases behaved as expected (21 passed, 0 rejected with a clear message).
