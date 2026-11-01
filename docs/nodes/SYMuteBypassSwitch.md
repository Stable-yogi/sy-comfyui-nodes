# MuteBypassSwitch SY (`SYMuteBypassSwitch`)

Source: `nodes/sy_mute_bypass_switch.py`

**What it does:** One switch for the nodes you choose. Select nodes on the canvas and press Add selected nodes. On runs them, off mutes them (they stop) or bypasses them (the data passes through). Give two or more switches the same pair name and only one of them can be on at a time. It has no wires itself.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| on | BOOLEAN | yes | On runs the chosen nodes. Off mutes or bypasses them. | default True |
| off_mode | COMBO | yes | What off does. Mute stops the node. Bypass lets the data pass through it. | one of: mute, bypass |
| pair | STRING | no | Same pair name on several switches = radio buttons: one on turns the others off. Empty = free switch. | default '' |

Outputs: none

## How to use

1. Add Mute/Bypass Switch SY anywhere in the workflow. It has no wires.
2. Select the nodes you want to control on the canvas, then press **Add selected nodes** on the switch. Press it again later to add more. The switch itself is never added.
3. Turn **on** off: the chosen nodes are muted (they stop) or bypassed (the data passes straight through), as set in **off_mode**. Turn it on again and they run.
4. The button under the switch shows how many nodes it controls (and how many are missing because they were deleted). Press it to select those nodes on the canvas. **Clear** forgets them and leaves them as they are.
5. Give two or more switches the same **pair** name and they work like radio buttons: turning one on turns the others off. Capitals and spaces do not matter.
6. The chosen nodes are saved with the workflow. Opening a workflow changes nothing until you flip the switch.
Fast Toggle SY switches many nodes from one panel. This node is one small switch per set of nodes that you can place next to them.
