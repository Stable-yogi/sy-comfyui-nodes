# Group Picker SY (`SYGroupPicker`)

Source: `nodes/sy_group_picker.py`

**What it does:** Pick one group of the workflow. Its nodes switch on and the nodes of the other groups switch off (mute or bypass). The choice is saved with the workflow and put back when you open it. Nodes outside the listed groups are never touched. The output is the name of the chosen group.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| choice | STRING | yes | The title of the chosen group. Set it by clicking in the list. | default '' |
| title_filter | STRING | yes | Only list groups whose title has this text. Empty lists all groups. | default '' |
| off_mode | COMBO | yes | Mute stops the node. Bypass passes data through. | one of: bypass, mute |
| bypass_words | STRING | yes | Comma list. A node with one of these words in its title is bypassed instead of muted. Example: image | default '' |
| apply_on_open | BOOLEAN | yes | Put the choice back when the workflow opens. | default True |

Outputs: `STRING`

The output is `choice`, the name of the picked group, as text.

## How to use

1. Put the parts of your workflow in groups and give each group a clear title (for example the name of a model family).
2. Add Group Picker SY. It lists the groups. Click one: its nodes switch on and the nodes of the other listed groups switch off.
3. **off_mode** is how the other groups switch off: mute stops the node, bypass passes data through. **bypass_words** is a comma list; a node with one of those words in its title (for example `image`) is bypassed even when off_mode is mute, so a switch further down can take the picture from the other source.
4. **title_filter** lists only the groups whose title has that text. Only the listed groups are switched. A node outside them, such as a shared seed or the Save Image node, is never touched.
5. The pick is saved with the workflow. When the workflow opens, the pick is put back (turn **apply_on_open** off to keep the nodes as they were saved). Set and Get nodes and subgraph nodes inside a group switch with it.
6. If you rename the picked group, the panel says no group has that name. Click the group again.

Group Switch SY and Group Picker SY should not control the same groups: they would undo each other.
