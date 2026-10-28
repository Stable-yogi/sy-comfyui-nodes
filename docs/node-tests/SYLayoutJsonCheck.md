# Layout JSON Check SY (`SYLayoutJsonCheck`)

Source: `nodes/sy_layout_json_check.py`

**What it does:** Checks a list of layout boxes: valid JSON, numbers, inside the picture, real size, short labels. Gives true or false and a report.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| layout_boxes | STRING | yes | The box list as JSON text. Connect a Layout Box or Merge node, or paste it. | default '', multiline |
| canvas_width | INT | yes | Width of the picture the boxes must fit in, in pixels. | 1 to 16384, default 1024 |
| canvas_height | INT | yes | Height of the picture the boxes must fit in, in pixels. | 1 to 16384, default 1024 |
| warn_overlap | BOOLEAN | yes | Add a warning when two boxes cover the same area. A warning does not make it invalid. | default True |

Outputs: `BOOLEAN`, `STRING`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | BOOLEAN=bool False; STRING=str 'INVALID: the box text is empty. Connect a Layout Box node or paste a JSON list.'; STRING=str '' |
| 2 | layout_boxes = '' (empty) | PASS | BOOLEAN=bool False; STRING=str 'INVALID: the box text is empty. Connect a Layout Box node or paste a JSON list.'; STRING=str '' |
| 3 | canvas_width = 1 (min) | PASS | BOOLEAN=bool False; STRING=str 'INVALID: the box text is empty. Connect a Layout Box node or paste a JSON list.'; STRING=str '' |
| 4 | canvas_width = 16384 (max) | PASS | BOOLEAN=bool False; STRING=str 'INVALID: the box text is empty. Connect a Layout Box node or paste a JSON list.'; STRING=str '' |
| 5 | canvas_width = 8192 (mid) | PASS | BOOLEAN=bool False; STRING=str 'INVALID: the box text is empty. Connect a Layout Box node or paste a JSON list.'; STRING=str '' |
| 6 | canvas_height = 1 (min) | PASS | BOOLEAN=bool False; STRING=str 'INVALID: the box text is empty. Connect a Layout Box node or paste a JSON list.'; STRING=str '' |
| 7 | canvas_height = 16384 (max) | PASS | BOOLEAN=bool False; STRING=str 'INVALID: the box text is empty. Connect a Layout Box node or paste a JSON list.'; STRING=str '' |
| 8 | canvas_height = 8192 (mid) | PASS | BOOLEAN=bool False; STRING=str 'INVALID: the box text is empty. Connect a Layout Box node or paste a JSON list.'; STRING=str '' |
| 9 | warn_overlap = False | PASS | BOOLEAN=bool False; STRING=str 'INVALID: the box text is empty. Connect a Layout Box node or paste a JSON list.'; STRING=str '' |

## Verdict

All 9 cases behaved as expected (9 passed, 0 rejected with a clear message).
