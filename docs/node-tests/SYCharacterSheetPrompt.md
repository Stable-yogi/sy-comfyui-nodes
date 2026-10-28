# CharacterSheetPrompt SY (`SYCharacterSheetPrompt`)

Source: `nodes/sy_character_sheet_prompt.py`

**What it does:** Writes a prompt that asks for a character reference sheet with the views you pick, with the same face and outfit in each view.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| character | STRING | yes | Describe the character: looks, clothes, age, anything that must stay the same. | default '', multiline |
| front | BOOLEAN | yes | Include a front view. | default True |
| side | BOOLEAN | yes | Include a side view. | default True |
| back | BOOLEAN | yes | Include a back view. | default True |
| three_quarter | BOOLEAN | yes | Include a three-quarter view. | default False |
| face_close_up | BOOLEAN | yes | Include a close-up of the face. | default False |
| full_body | BOOLEAN | yes | Include a full-body shot. | default False |
| background | COMBO | yes | The background behind the character. | one of: plain_white, plain_grey, transparent_look, none |
| layout | COMBO | yes | Put the views in a grid or in one row. | one of: grid, row |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: character is empty: describe the person or creature |
| 2 | character = '' (empty) | REJECTED | ValueError: character is empty: describe the person or creature |
| 3 | front = False | REJECTED | ValueError: character is empty: describe the person or creature |
| 4 | side = False | REJECTED | ValueError: character is empty: describe the person or creature |
| 5 | back = False | REJECTED | ValueError: character is empty: describe the person or creature |
| 6 | three_quarter = True | REJECTED | ValueError: character is empty: describe the person or creature |
| 7 | face_close_up = True | REJECTED | ValueError: character is empty: describe the person or creature |
| 8 | full_body = True | REJECTED | ValueError: character is empty: describe the person or creature |
| 9 | background = 'plain_grey' | REJECTED | ValueError: character is empty: describe the person or creature |
| 10 | background = 'transparent_look' | REJECTED | ValueError: character is empty: describe the person or creature |
| 11 | background = 'none' | REJECTED | ValueError: character is empty: describe the person or creature |
| 12 | layout = 'row' | REJECTED | ValueError: character is empty: describe the person or creature |

## Verdict

All 12 cases behaved as expected (0 passed, 12 rejected with a clear message).
