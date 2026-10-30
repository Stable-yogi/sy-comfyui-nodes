# Text Stats SY (`SYTextStats`)

Source: `nodes/sy_text_stats.py`

**What it does:** Counts the characters, words and lines of a text and guesses the tokens (characters divided by 4).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to count. It passes nothing on, it only measures. | default '', multiline |

Outputs: `INT`, `INT`, `INT`, `INT`, `STRING`
