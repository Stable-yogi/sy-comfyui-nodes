# Assert SY (`SYAssert`)

Source: `nodes/sy_assert.py`

**What it does:** Stops the whole run with your message when the value is no. Use it to catch a wrong setting before the slow part starts.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| condition | BOOLEAN | yes | Must be yes for the run to go on. No stops the run. | default True |
| message | STRING | yes | The text shown when the run stops. | default 'Assert failed: the value was no.' |

Outputs: `BOOLEAN`
