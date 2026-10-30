# Multiline Text SY (`SYMultilineText`)

Source: `nodes/sy_multiline_text.py`

**What it does:** A big text box. Lines starting with # are notes to yourself and are left out. Start a line with \# to keep a #.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Your text. Lines that start with # are ignored. | default '', multiline |
| keep_empty_lines | BOOLEAN | yes | Off: also remove empty lines from the result. | default True |

Outputs: `STRING`
