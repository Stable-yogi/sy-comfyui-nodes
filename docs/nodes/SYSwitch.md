# Switch SY (`SYSwitch`)

Source: `nodes/sy_switch.py`

**What it does:** One switch, two inputs. On sends input A. Off sends input B. The branch you do not pick is not run.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| use_a | BOOLEAN | yes | On sends input A. Off sends input B. | default True |
| a | * | no | Sent when the switch is on. |  |
| b | * | no | Sent when the switch is off. |  |

Outputs: `*`

## How to use

1. Connect one thing to a and another to b. They can be any type.
2. Turn use_a on to send a, off to send b.
3. The branch you do not pick is not run.
