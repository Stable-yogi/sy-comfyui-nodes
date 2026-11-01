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

## How to use

1. Add the node to the workflow. It lists the groups of the workflow, each with an on/off switch. It runs nothing itself and has no outputs.
2. Use title_filter to list only groups whose title has some text. Choose sort: by position on the canvas or alphabetical.
3. Switching a group off turns all nodes in it off. off_mode picks bypass (data passes through) or mute (the node stops).
4. Turn on one_at_a_time so that switching one group on switches all the others off.
