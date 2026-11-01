# JSON From Reply SY (`SYJSONFromReply`)

Source: `nodes/sy_json_from_reply.py`

**What it does:** Finds the JSON {...} or [...] in a chatty text reply, fixes trailing commas, and gives clean JSON. Pick the first, the last or the biggest block, get it pretty-printed, and optionally repair Python-style replies (single quotes, True/None). An info line says what was found.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The reply that contains JSON somewhere inside it. | default '', multiline |
| sorted_keys | BOOLEAN | yes | On: sort the keys of every object alphabetically. | default False |
| raise_if_missing | BOOLEAN | yes | On: stop with an error if no JSON is found. Off: give empty text and found = false. | default True |
| which | COMBO | no | When the reply holds several JSON blocks: take the first, the last (often the final answer) or the biggest. | one of: first, last, largest |
| pretty | BOOLEAN | no | On: give the JSON spread over several lines, easier to read. Off: one compact line. | default False |
| python_style | BOOLEAN | no | On: also accept replies written Python style, like {'a': True, 'b': None}. | default False |

Outputs: `STRING`, `BOOLEAN`, `STRING`
