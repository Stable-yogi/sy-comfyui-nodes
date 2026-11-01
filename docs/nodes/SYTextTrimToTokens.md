# Text Trim To Tokens SY (`SYTextTrimToTokens`)

Source: `nodes/sy_text_trim_to_tokens.py`

**What it does:** Cuts a text to a rough token budget, counting 4 characters as 1 token. Keep the start, the end or the middle. Can cut at a whole word or a whole comma tag so no word is chopped in half, and the info line says what was cut.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to shorten. | default '', multiline |
| max_tokens | INT | yes | Token budget. One token is counted as 4 characters. | 1 to 1000000, default 256 |
| keep | COMBO | yes | Which part survives when the text is too long. | one of: start, end, middle |
| cut_at | COMBO | no | Where the cut may fall: anywhere, between words, or between comma tags. | one of: exact characters, whole words, whole tags (commas) |

Outputs: `STRING`, `INT`, `BOOLEAN`, `STRING`
