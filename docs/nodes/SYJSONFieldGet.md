# JSON Field Get SY (`SYJSONFieldGet`)

Source: `nodes/sy_json_field_get.py`

**What it does:** Reads one value from a JSON text. The path is dots between keys, and numbers pick list items, like a.b.0. A missing key can give a fallback value instead of stopping, a JSON wrapped in ``` fences is accepted, and it also tells if the key was found and what type the value is.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| json_text | STRING | yes | The JSON text to read from. | default '', multiline |
| path | STRING | yes | Keys joined by dots, numbers for list items, like a.b.0. Empty gives it all. | default '' |
| if_missing | COMBO | no | What to do when the path is not in the JSON: stop with a message, or give the default value. | one of: error, use default |
| default_value | STRING | no | Value given when the path is missing and if_missing is use default. Can be empty. | default '' |

Outputs: `STRING`, `BOOLEAN`, `STRING`
