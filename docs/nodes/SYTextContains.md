# Text Contains SY (`SYTextContains`)

Source: `nodes/sy_text_contains.py`

**What it does:** Checks if a text contains a word or phrase. Gives true or false, and passes the text through.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to look in. It also comes out unchanged. | default '', multiline |
| needle | STRING | yes | The word or phrase to look for. | default '' |
| case_sensitive | BOOLEAN | yes | On: upper and lower case must match exactly. | default False |

Outputs: `BOOLEAN`, `STRING`
