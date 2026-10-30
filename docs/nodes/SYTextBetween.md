# Text Between SY (`SYTextBetween`)

Source: `nodes/sy_text_between.py`

**What it does:** Cuts out the text between a start marker and an end marker. Stops with a clear error if a marker is missing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to search in. | default '', multiline |
| start_marker | STRING | yes | The text just before the part you want. | default '' |
| end_marker | STRING | yes | The text just after the part you want. | default '' |
| which | COMBO | yes | If the pair appears many times: take the first one or the last one. | one of: first, last |
| include_markers | BOOLEAN | yes | On: keep the start and end markers in the result. | default False |
| case_sensitive | BOOLEAN | yes | On: capital letters must match. Off: they are ignored. | default True |

Outputs: `STRING`
