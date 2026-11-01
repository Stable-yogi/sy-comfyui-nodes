# Multiline Text SY (`SYMultilineText`)

Source: `nodes/sy_multiline_text.py`

**What it does:** A big text box. Lines starting with # are notes to yourself and are left out. Start a line with \# to keep a #. Optional tidying: trim lines, collapse spaces, drop repeated lines, cut ' # note' endings. Also gives the line count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Your text. Lines that start with # are ignored. | default '', multiline |
| keep_empty_lines | BOOLEAN | yes | Off: also remove empty lines from the result. | default True |
| trim_lines | BOOLEAN | no | On: remove spaces at the start and end of each line. | default False |
| collapse_spaces | BOOLEAN | no | On: turn runs of spaces inside a line into one space. | default False |
| drop_duplicate_lines | BOOLEAN | no | On: remove a line that already appeared (any case). Empty lines stay. | default False |
| inline_comments | BOOLEAN | no | On: cut the end of a line from ' #' onward, so 'a cat # old' becomes 'a cat'. | default False |

Outputs: `STRING`, `INT`, `STRING`
