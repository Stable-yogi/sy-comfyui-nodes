# Control Panel SY (`SYControlPanel`)

Source: `nodes/sy_control_panel.py`

**What it does:** One panel for the settings you change most. Every row is a dial with its own name and its own range: a number, a whole number, a switch, a text, a dropdown with your own list, or a seed. The range is yours, so you can go as high or low as you like, and typing a number is never cut off. Each row is one output; connect it to any input. 'Take widgets from nodes' moves the widgets of other nodes into the panel and connects them for you.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| rows | STRING | yes | The rows of the panel. The panel on the node fills this in; you do not type it. | default '[]' |

Outputs: one output for each row, up to 32 (`out1` to `out32`). The output of a row is named like the row and has the type of its kind: a number gives FLOAT, a whole number or a seed gives INT, a switch gives BOOLEAN, a text or a dropdown gives STRING.

## How to use

1. Add a row with **Add row**, or press **Take widgets from nodes**, tick the widgets you want (for example the steps, cfg and seed of a sampler) and press the add button. Each one becomes a row and is connected to its node.
2. Give each row its own name. Pick the kind: Number, Whole number, Switch, Text, Dropdown or Seed.
3. **settings** on a row opens its lowest, highest and step values (the slider range) or, for a dropdown, its list. The range only sets the slider. You can type any number in the box and it is never cut off.
4. A seed row can stay fixed, pick a new random number each run, or count up by one each run. After a run the box shows the seed that was used.
5. **up** and **down** move a row and its wire together. **X** deletes the row and its wire.
