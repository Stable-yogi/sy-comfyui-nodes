# Text Join SY (`SYTextJoin`)

Source: `nodes/sy_text_join.py`

**What it does:** Joins up to six texts into one, with a separator between them. Empty texts can be skipped, spaces around each part can be trimmed, and a part that repeats an earlier one can be dropped. The info line says how many were joined.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| separator | STRING | yes | What goes between the texts. A comma and space is common. | default ', ' |
| skip_empty | BOOLEAN | yes | On: empty texts are left out so you get no double separators. | default True |
| text_a | STRING | no | The first text to join. Leave empty to skip it. | default '', multiline |
| text_b | STRING | no | The second text to join. Leave empty to skip it. | default '', multiline |
| text_c | STRING | no | The third text to join. Leave empty to skip it. | default '', multiline |
| text_d | STRING | no | The fourth text to join. Leave empty to skip it. | default '', multiline |
| text_e | STRING | no | The fifth text to join. Leave empty to skip it. | default '', multiline |
| text_f | STRING | no | The sixth text to join. Leave empty to skip it. | default '', multiline |
| trim_parts | BOOLEAN | no | On: remove spaces and line breaks around each text before joining. | default False |
| remove_repeats | BOOLEAN | no | On: a text that is the same as an earlier one (capitals ignored) is left out. | default False |

Outputs: `STRING`, `STRING`

## How to use

1. Connect up to six texts to text_a to text_f.
2. Set separator (a comma and space is common). Leave skip_empty on to avoid double separators.
3. Optional: turn on trim_parts and remove_repeats.
4. The joined text and an info line come out.
