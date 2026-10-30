# Text Join SY (`SYTextJoin`)

Source: `nodes/sy_text_join.py`

**What it does:** Joins up to four texts into one, with a separator between them. Empty texts can be skipped.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| separator | STRING | yes | What goes between the texts. A comma and space is common. | default ', ' |
| skip_empty | BOOLEAN | yes | On: empty texts are left out so you get no double separators. | default True |
| text_a | STRING | no | The first text to join. Leave empty to skip it. | default '', multiline |
| text_b | STRING | no | The second text to join. Leave empty to skip it. | default '', multiline |
| text_c | STRING | no | The third text to join. Leave empty to skip it. | default '', multiline |
| text_d | STRING | no | The fourth text to join. Leave empty to skip it. | default '', multiline |

Outputs: `STRING`
