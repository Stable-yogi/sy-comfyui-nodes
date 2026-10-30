# JSON Field Get SY (`SYJSONFieldGet`)

Source: `nodes/sy_json_field_get.py`

**What it does:** Reads one value from a JSON text. The path is dots between keys, and numbers pick list items, like a.b.0.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| json_text | STRING | yes | The JSON text to read from. | default '', multiline |
| path | STRING | yes | Keys joined by dots, numbers for list items, like a.b.0. Empty gives it all. | default '' |

Outputs: `STRING`
