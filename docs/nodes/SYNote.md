# Note SY (`SYNote`)

Source: `nodes/sy_note.py`

**What it does:** A note card for your workflow. Pick a style and the card gets a colour. The text can also go out as a prompt.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Write your note here. Plain text. | default '', multiline |
| style | COMBO | yes | Info is blue, tip is green, warning is red, step is gold, model is purple. | one of: info, tip, warning, step, model |

Outputs: `STRING`
