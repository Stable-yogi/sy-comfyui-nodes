# Text Between SY (`SYTextBetween`)

Source: `nodes/sy_text_between.py`

**What it does:** Cuts out the text between a start marker and an end marker, for example to pull an answer out of chatty model output. A missing marker stops with a clear error, or gives empty or the whole text if you choose. Can trim the result.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to search in. | default '', multiline |
| start_marker | STRING | yes | The text just before the part you want. | default '' |
| end_marker | STRING | yes | The text just after the part you want. | default '' |
| which | COMBO | yes | If the pair appears many times: take the first one or the last one. | one of: first, last |
| include_markers | BOOLEAN | yes | On: keep the start and end markers in the result. | default False |
| case_sensitive | BOOLEAN | yes | On: capital letters must match. Off: they are ignored. | default True |
| if_missing | COMBO | no | When a marker is not found: stop with an error, give empty text, or pass the whole text through. | one of: stop with an error, give empty text, give the whole text |
| trim_result | BOOLEAN | no | On: remove spaces and empty lines around the result. | default False |

Outputs: `STRING`, `STRING`
