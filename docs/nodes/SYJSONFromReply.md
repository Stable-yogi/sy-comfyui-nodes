# JSON From Reply SY (`SYJSONFromReply`)

Source: `nodes/sy_json_from_reply.py`

**What it does:** Finds the first {...} or [...] in a text reply, fixes trailing commas, and gives clean compact JSON.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The reply that contains JSON somewhere inside it. | default '', multiline |
| sorted_keys | BOOLEAN | yes | On: sort the keys of every object alphabetically. | default False |
| raise_if_missing | BOOLEAN | yes | On: stop with an error if no JSON is found. Off: give empty text and found = false. | default True |

Outputs: `STRING`, `BOOLEAN`
