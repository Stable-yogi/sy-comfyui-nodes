# Text Chunker SY (`SYTextChunker`)

Source: `nodes/sy_text_chunker.py`

**What it does:** Splits a long text into pieces of at most a set number of characters, with overlap. Gives you one piece by index, and the piece count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The long text to split. | default '', multiline |
| max_chars | INT | yes | Longest allowed piece, in characters. | 1 to 1000000, default 1000 |
| overlap | INT | yes | Characters repeated at the start of the next piece. Less than max_chars. | 0 to 999999, default 100 |
| index | INT | yes | Which piece to output, counting from 0. | 0 to 1000000, default 0 |

Outputs: `STRING`, `INT`
