# Label SY (`SYLabel`)

Source: `nodes/sy_label.py`

**What it does:** A big text label that floats in your workflow, like a sticker for a title or a step name. Pick the size, colour and side. It runs nothing and has no wires.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The words to show. Use Enter for a new line. | default 'Label', multiline |
| size | INT | yes | Height of the letters in pixels. | 10 to 200, default 36 |
| colour | COMBO | yes | Colour of the letters. | one of: gold, white, grey, blue, green, red, purple |
| align | COMBO | yes | Where the words sit inside the label. | one of: left, centre, right |

Outputs: none

## How to use

1. Add Label SY anywhere in the workflow. It has no wires.
2. Type your words in text (Enter starts a new line).
3. Set size (height of the letters), colour and align (left, centre or right). The label redraws at once.
Use it for titles and step names. It runs nothing and costs no time.
