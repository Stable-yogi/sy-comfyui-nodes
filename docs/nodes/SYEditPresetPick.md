# EditPresetPick SY (`SYEditPresetPick`)

Source: `nodes/sy_edit_preset_pick.py`

**What it does:** Gives ready-made wording for common picture edits like fixing light or removing the background. Your own text replaces it if you type any.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | The ready-made edit wording to use. | one of: remove_object, fix_lighting, colourise_black_and_white, make_it_daytime, make_it_night, remove_background_to_white, sharpen_and_clean, change_season_to_winter |
| custom_override | STRING | no | If you type anything here, it is used instead of the preset. | default '', multiline |

Outputs: `STRING`
