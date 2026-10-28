# TextInImage SY (`SYTextInImage`)

Source: `nodes/sy_text_in_image.py`

**What it does:** Writes a phrase that asks for exact words to appear in the picture at a place you choose. The words are put in double quotes.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The exact words to show. Do not type double quote marks. | default '' |
| placement | COMBO | yes | Where the words should appear. | one of: top, centre, bottom, left, right, on_sign, on_shirt, on_poster |
| style_words | STRING | no | How the letters look, for example 'bold white capital letters'. | default '' |
| language_hint | STRING | no | Optional language name, for example 'German'. | default '' |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: text is empty: type the words that should appear in the picture |
| 2 | text = '' (empty) | REJECTED | ValueError: text is empty: type the words that should appear in the picture |
| 3 | placement = 'centre' | REJECTED | ValueError: text is empty: type the words that should appear in the picture |
| 4 | placement = 'bottom' | REJECTED | ValueError: text is empty: type the words that should appear in the picture |
| 5 | placement = 'left' | REJECTED | ValueError: text is empty: type the words that should appear in the picture |
| 6 | placement = 'right' | REJECTED | ValueError: text is empty: type the words that should appear in the picture |
| 7 | placement = 'on_sign' | REJECTED | ValueError: text is empty: type the words that should appear in the picture |
| 8 | placement = 'on_shirt' | REJECTED | ValueError: text is empty: type the words that should appear in the picture |
| 9 | placement = 'on_poster' | REJECTED | ValueError: text is empty: type the words that should appear in the picture |
| 10 | style_words = '' (empty) | REJECTED | ValueError: text is empty: type the words that should appear in the picture |
| 11 | language_hint = '' (empty) | REJECTED | ValueError: text is empty: type the words that should appear in the picture |

## Verdict

All 11 cases behaved as expected (0 passed, 11 rejected with a clear message).
