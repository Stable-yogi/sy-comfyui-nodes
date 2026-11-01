# JSON Prompt Builder SY (`SYJSONPromptBuilder`)

Source: `nodes/sy_json_prompt_builder.py`

**What it does:** Turns lines like 'subject: a fox' into a valid JSON text. Quotes and special characters are escaped for you. Can also build groups from keys like camera.angle, turn 'a | b | c' into a list, and an info line counts the keys.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| lines | STRING | yes | One key: value per line. Lines starting with # are skipped. | default 'subject: a fox\nmood: calm', multiline |
| auto_types | BOOLEAN | yes | On: true, false, null and numbers become real JSON values. Off: all text. | default True |
| indent | INT | yes | Spaces per level. 0 gives one compact line. | 0 to 8, default 2 |
| nest_dots | BOOLEAN | no | On: a key like camera.angle becomes a group: {"camera": {"angle": ...}}. | default False |
| list_separator | STRING | no | A mark that splits a value into a list, for example \| so that tags: a \| b gives ["a", "b"]. Empty: off. | default '' |

Outputs: `STRING`, `STRING`

## How to use

1. Type one key: value per line in lines. Lines starting with # are skipped.
2. auto_types on turns true, false, null and numbers into real JSON values. Quotes and special characters are escaped for you.
3. Optional: nest_dots turns a key like camera.angle into a group, and list_separator (for example |) turns tags: a | b into a list. indent sets spaces per level; 0 gives one line.
4. The JSON text and an info line that counts the keys come out.
