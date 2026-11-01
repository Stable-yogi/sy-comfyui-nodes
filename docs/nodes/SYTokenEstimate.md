# Token Estimate SY (`SYTokenEstimate`)

Source: `nodes/sy_token_estimate.py`

**What it does:** Gives a rough word, character and token count. The token number is only an estimate, not what a real tokenizer would say. Set a token limit to get a true or false for going over it, and the info line shows how many 75-token pieces a CLIP encoder needs.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to measure. | default '', multiline |
| token_limit | INT | no | Your limit in tokens, for example 77 or 225. 0 means no limit. | 0 to 10000000, default 0 |

Outputs: `INT`, `INT`, `INT`, `BOOLEAN`, `STRING`
