# If Else Text SY (`SYIfElseText`)

Source: `nodes/sy_if_else_text.py`

**What it does:** Picks one of two texts. Yes sends if_true. No sends if_false. Can use the other text when the chosen one is empty, and tells you which one it sent.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| condition | BOOLEAN | yes | Yes sends if_true. No sends if_false. | default True |
| if_true | STRING | yes | The text sent when the condition is yes. | default '', multiline |
| if_false | STRING | yes | The text sent when the condition is no. | default '', multiline |
| fallback_when_empty | BOOLEAN | no | On sends the other text when the chosen one is empty or only spaces. | default False |

Outputs: `STRING`, `STRING`

## How to use

1. Connect or set condition (yes or no) and the two texts if_true and if_false.
2. Yes sends if_true. No sends if_false.
3. Turn on fallback_when_empty to send the other text when the chosen one is empty or only spaces.
4. The chosen text comes out, plus a line that says which one was sent.
