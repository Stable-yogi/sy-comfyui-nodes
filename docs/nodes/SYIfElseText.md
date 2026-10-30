# If Else Text SY (`SYIfElseText`)

Source: `nodes/sy_if_else_text.py`

**What it does:** Picks one of two texts. Yes sends if_true. No sends if_false.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| condition | BOOLEAN | yes | Yes sends if_true. No sends if_false. | default True |
| if_true | STRING | yes | The text sent when the condition is yes. | default '', multiline |
| if_false | STRING | yes | The text sent when the condition is no. | default '', multiline |

Outputs: `STRING`
