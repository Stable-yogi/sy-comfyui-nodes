# JSON Prompt Builder SY (`SYJSONPromptBuilder`)

Source: `nodes/sy_json_prompt_builder.py`

**What it does:** Turns lines like 'subject: a fox' into a valid JSON text. Quotes and special characters are escaped for you.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| lines | STRING | yes | One key: value per line. Lines starting with # are skipped. | default 'subject: a fox\nmood: calm', multiline |
| auto_types | BOOLEAN | yes | On: true, false, null and numbers become real JSON values. Off: all text. | default True |
| indent | INT | yes | Spaces per level. 0 gives one compact line. | 0 to 8, default 2 |

Outputs: `STRING`
