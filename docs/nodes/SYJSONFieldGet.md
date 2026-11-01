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

## How to use

1. Connect or paste the JSON text in json_text. A JSON wrapped in ``` fences is accepted.
2. Type path with dots between keys and numbers for list items, like a.b.0. An empty path gives all of it.
3. Set if_missing: error stops with a message, use default gives default_value instead.
4. You get the value as text, a true or false for whether the key was found, and its type.
