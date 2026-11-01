# Note SY (`SYNote`)

Source: `nodes/sy_note.py`

**What it does:** A note card for your workflow. Pick a style and the card gets a colour. The text can also go out as a prompt, with the style in front if you like, and an info line counts the words.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Write your note here. Plain text. | default '', multiline |
| style | COMBO | yes | Info is blue, tip is green, warning is red, step is gold, model is purple. | one of: info, tip, warning, step, model |
| add_style_label | BOOLEAN | no | On puts the style in front of the sent text, for example WARNING: check the seed. | default False |
| trim | BOOLEAN | no | On cuts spaces and blank lines from the start and end of the sent text. | default False |

Outputs: `STRING`, `STRING`

## How to use

1. Type your note in text and pick a style. The card colour follows it: info blue, tip green, warning red, step gold, model purple.
2. The text can also be sent on as a prompt. Turn add_style_label on to put the style word in front, for example WARNING: check the seed. Turn trim on to cut spaces and blank lines at the ends.
3. Outputs: the text and an info line with the word count.
