# EditPresetPick SY (`SYEditPresetPick`)

Source: `nodes/sy_edit_preset_pick.py`

**What it does:** Gives ready-made wording for common picture edits like fixing light or removing the background. Your own text replaces it if you type any.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | The ready-made edit wording to use. | one of: remove_object, fix_lighting, colourise_black_and_white, make_it_daytime, make_it_night, remove_background_to_white, sharpen_and_clean, change_season_to_winter |
| custom_override | STRING | no | If you type anything here, it is used instead of the preset. | default '', multiline |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'Remove the unwanted object from the picture and fill the gap so it looks natu...' |
| 2 | preset = 'fix_lighting' | PASS | STRING=str 'Fix the lighting so the scene is evenly lit, with soft natural light and no h...' |
| 3 | preset = 'colourise_black_and_white' | PASS | STRING=str 'Turn this black and white picture into a natural full-colour picture.' |
| 4 | preset = 'make_it_daytime' | PASS | STRING=str 'Change the scene so it is bright daytime with a clear sky and natural sunlight.' |
| 5 | preset = 'make_it_night' | PASS | STRING=str 'Change the scene so it is night time, dark and lit by moonlight and soft lamps.' |
| 6 | preset = 'remove_background_to_white' | PASS | STRING=str 'Remove the background and put the subject on a plain white background.' |
| 7 | preset = 'sharpen_and_clean' | PASS | STRING=str 'Make the picture sharper and cleaner by removing blur, noise and small marks.' |
| 8 | preset = 'change_season_to_winter' | PASS | STRING=str 'Change the season to winter with snow on the ground and bare, frosty trees.' |
| 9 | custom_override = '' (empty) | PASS | STRING=str 'Remove the unwanted object from the picture and fill the gap so it looks natu...' |

## Verdict

All 9 cases behaved as expected (9 passed, 0 rejected with a clear message).
