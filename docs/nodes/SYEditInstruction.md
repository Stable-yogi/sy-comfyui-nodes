# EditInstruction SY (`SYEditInstruction`)

Source: `nodes/sy_edit_instruction.py`

**What it does:** Writes one clear sentence for an image edit model, such as 'Replace the hat with a red cap.' It can add a line to keep the rest unchanged.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| action | COMBO | yes | What kind of change you want. | one of: replace, remove, add, recolour, restyle, change_background, fix_lighting |
| target | STRING | yes | The part of the picture to change, for example 'red hat'. | default '' |
| keep_rest | BOOLEAN | yes | Adds a line asking the model to leave everything else alone. | default True |
| to_value | STRING | no | What it should become. Needed for every action except remove and fix_lighting. | default '' |
| extra | STRING | no | Optional extra detail added after the main sentence. | default '' |

Outputs: `STRING`
