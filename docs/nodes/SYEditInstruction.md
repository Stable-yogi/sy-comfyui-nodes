# EditInstruction SY (`SYEditInstruction`)

Source: `nodes/sy_edit_instruction.py`

**What it does:** Writes one clear sentence for an image edit model, such as 'Replace the hat with a red cap.' It can add a line to keep the rest unchanged, or to keep one named thing (for example the face). A notes line warns about ignored or too long input.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| action | COMBO | yes | What kind of change you want. | one of: replace, remove, add, recolour, restyle, change_background, fix_lighting |
| target | STRING | yes | The part of the picture to change, for example 'red hat'. | default '' |
| keep_rest | BOOLEAN | yes | Adds a line asking the model to leave everything else alone. | default True |
| to_value | STRING | no | What it should become. Needed for every action except remove and fix_lighting. | default '' |
| extra | STRING | no | Optional extra detail added after the main sentence. | default '' |
| keep_detail | STRING | no | Name what must not change, for example: the face and the pose. | default '' |

Outputs: `STRING`, `STRING`

## How to use

1. Pick action: replace, remove, add, recolour, restyle, change_background or fix_lighting.
2. Type the thing in target, and the new value in to_value where it applies.
3. keep_rest adds a line to keep the rest unchanged. keep_detail names one thing to keep. extra adds more words.
4. The sentence comes out as instruction. notes warns about ignored or too long input.
