# Assert SY (`SYAssert`)

Source: `nodes/sy_assert.py`

**What it does:** Stops the whole run with your message when the value is no. Use it to catch a wrong setting before the slow part starts. Has an on/off switch, so you can leave it in the workflow.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| condition | BOOLEAN | yes | Must be yes for the run to go on. No stops the run. | default True |
| message | STRING | yes | The text shown when the run stops. Say what is wrong and how to fix it. | default 'Assert failed: the value was no.' |
| enabled | BOOLEAN | no | Off skips the check and lets the run go on. Handy to test without deleting the node. | default True |

Outputs: `BOOLEAN`, `STRING`
