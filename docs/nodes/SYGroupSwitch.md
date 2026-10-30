# GroupSwitch SY (`SYGroupSwitch`)

Source: `nodes/sy_group_switch.py`

**What it does:** Shows every group of the workflow with an on/off switch. Off turns all nodes in that group off (bypass or mute). Use it to switch whole parts of a workflow, like an upscale part, with one click. It runs nothing itself.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| title_filter | STRING | yes | Only list groups whose title has this text. Empty lists all groups. | default '' |
| off_mode | COMBO | yes | Bypass passes data through. Mute stops the node. | one of: bypass, mute |
| sort | COMBO | yes | Order of the list: top to bottom on the canvas, or by title. | one of: position, alphabetical |
| one_at_a_time | BOOLEAN | yes | When on, switching one group on switches all others off. | default False |

Outputs: none
