# JSON To Lines SY (`SYJSONToLines`)

Source: `nodes/sy_json_to_lines.py`

**What it does:** Turns JSON text into plain lines, one value per line. Lists become key[0], key[1]. Very deep parts are written as short one-line JSON.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| json_text | STRING | yes | The JSON to turn into lines. | default '', multiline |
| format | COMBO | yes | How each line looks. Dotted shows the whole path, like a.b.0. | one of: key: value, key = value, value only, dotted.path: value |
| max_depth | INT | yes | Levels to open up. Deeper parts become one line of JSON. | 1 to 10, default 4 |
| sort_keys | BOOLEAN | yes | On: list the keys in alphabetical order instead of file order. | default False |
| on_error | COMBO | yes | What to do with bad JSON: stop with a message, or give empty text. | one of: raise, empty text |

Outputs: `STRING`, `INT`

## How to use

1. Paste the JSON into **json_text**.
2. Pick the **format** you want for each line.
3. Set **max_depth** for how many levels to open up.
4. Turn on **sort_keys** if you want alphabetical order.
5. Use **text** for the lines. Bad JSON stops with "Invalid JSON: line, column" unless **on_error** is "empty text".
