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
