# Text Template SY (`SYTextTemplate`)

Source: `nodes/sy_text_template.py`

**What it does:** Fills {name} placeholders in a text with up to four named values. A name with no matching input gives an error.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| template | STRING | yes | Text with {name} placeholders to fill in. | default 'a photo of {name}, {style}', multiline |
| name_1 | STRING | no | Placeholder name for value 1, used as {name} in the template. | default 'name' |
| value_1 | STRING | no | Text that replaces the placeholder named in name_1. | default '' |
| name_2 | STRING | no | Placeholder name for value 2, used as {name} in the template. | default 'style' |
| value_2 | STRING | no | Text that replaces the placeholder named in name_2. | default '' |
| name_3 | STRING | no | Placeholder name for value 3, used as {name} in the template. | default '' |
| value_3 | STRING | no | Text that replaces the placeholder named in name_3. | default '' |
| name_4 | STRING | no | Placeholder name for value 4, used as {name} in the template. | default '' |
| value_4 | STRING | no | Text that replaces the placeholder named in name_4. | default '' |

Outputs: `STRING`
