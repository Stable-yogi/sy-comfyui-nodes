# IndexSwitch SY (`SYIndexSwitch`)

Source: `nodes/sy_index_switch.py`

**What it does:** Pick one of up to four inputs by number. Select 1 sends input1, select 2 sends input2, and so on. The inputs you do not pick are not run.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| select | INT | yes | Which input to send, from 1 to 4. | 1 to 4, step 1, default 1 |
| input1 | * | no | Sent when select is 1. |  |
| input2 | * | no | Sent when select is 2. |  |
| input3 | * | no | Sent when select is 3. |  |
| input4 | * | no | Sent when select is 4. |  |

Outputs: `*`, `INT`
