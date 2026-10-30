# Text Wrap SY (`SYTextWrap`)

Source: `nodes/sy_text_wrap.py`

**What it does:** Breaks long lines of text at a chosen width. Long words are split, and paragraphs can be kept apart.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to wrap. | default '', multiline |
| width | INT | yes | Most characters allowed on one line. | 4 to 1000, step 1, default 40 |
| keep_paragraphs | BOOLEAN | yes | On keeps a blank line between paragraphs. Off joins all the text into one block. | default True |

Outputs: `STRING`, `INT`
