# Text Diff Lines SY (`SYTextDiffLines`)

Source: `nodes/sy_text_diff_lines.py`

**What it does:** Compares two multi-line texts line by line. Shows the lines only in A, only in B and in both, with a one-line summary.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text_a | STRING | yes | The first text. One item per line. | default '', multiline |
| text_b | STRING | yes | The second text. One item per line. | default '', multiline |
| ignore_case | BOOLEAN | yes | On: Red and red count as the same line. | default False |
| trim_spaces | BOOLEAN | yes | On: spaces at the start and end of a line are ignored. | default True |

Outputs: `STRING`, `STRING`, `STRING`, `STRING`

## How to use

1. Put one list in **text_a** and another in **text_b**, one item per line.
2. Turn on **ignore_case** if Red and red should count as the same line.
3. Leave **trim_spaces** on to ignore spaces at the start and end of lines.
4. Read **only_a**, **only_b** and **both** for the three groups of lines, and **summary** for a one-line count.
