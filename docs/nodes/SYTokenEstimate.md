# Token Estimate SY (`SYTokenEstimate`)

Source: `nodes/sy_token_estimate.py`

**What it does:** Gives a rough word, character and token count. The token number is only an estimate, not what a real tokenizer would say.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to measure. | default '', multiline |

Outputs: `INT`, `INT`, `INT`
