# Text Truncate SY (`SYTextTruncate`)

Source: `nodes/sy_text_truncate.py`

**What it does:** Shortens a text to a maximum length and adds an ending such as three dots. Can cut at a word end.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to shorten. | default '', multiline |
| max_chars | INT | yes | Longest allowed result, counting the ending. | 1 to 100000, default 100 |
| suffix | STRING | yes | Added at the end when the text was cut. Leave empty for none. | default '...' |
| at_word | BOOLEAN | yes | On: cut back to the end of a whole word. Off: cut at the exact character. | default True |

Outputs: `STRING`, `BOOLEAN`
