# Text Chunker SY (`SYTextChunker`)

Source: `nodes/sy_text_chunker.py`

**What it does:** Splits a long text into pieces of at most a set number of characters, with overlap. Gives you one piece by index, the piece count and all pieces as a list. An index too big can wrap around instead of stopping.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The long text to split. | default '', multiline |
| max_chars | INT | yes | Longest allowed piece, in characters. | 1 to 1000000, default 1000 |
| overlap | INT | yes | Characters repeated at the start of the next piece. Less than max_chars. | 0 to 999999, default 100 |
| index | INT | yes | Which piece to output, counting from 0. | 0 to 1000000, default 0 |
| index_mode | COMBO | no | If index is past the last piece: stop with an error, start again at 0, or stay on the last piece. | one of: stop with an error, wrap around, stay on the last |

Outputs: `STRING`, `INT`, `STRING`, `STRING`
