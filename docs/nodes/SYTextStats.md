# Text Stats SY (`SYTextStats`)

Source: `nodes/sy_text_stats.py`

**What it does:** Counts the characters, words and lines of a text and guesses the tokens (characters divided by 4). Set a token limit (for example 77) to get a true or false for going over it, and a plain info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to count. It passes nothing on, it only measures. | default '', multiline |
| token_limit | INT | no | Your limit in tokens, for example 77 for a prompt. 0 means no limit. | 0 to 10000000, default 0 |

Outputs: `INT`, `INT`, `INT`, `INT`, `STRING`, `BOOLEAN`, `STRING`
