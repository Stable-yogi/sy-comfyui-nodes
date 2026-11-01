# EditPresetPick SY (`SYEditPresetPick`)

Source: `nodes/sy_edit_preset_pick.py`

**What it does:** Gives ready-made wording for common picture edits like fixing light, blurring or removing the background. Your own text replaces it if you type any, and an extra sentence can be added to either. An info line says which was used.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | The ready-made edit wording to use. | one of: remove_object, fix_lighting, colourise_black_and_white, make_it_daytime, make_it_night, remove_background_to_white, sharpen_and_clean, change_season_to_winter, remove_text_and_watermark, blur_background, golden_hour_light, turn_to_black_and_white |
| custom_override | STRING | no | If you type anything here, it is used instead of the preset. | default '', multiline |
| extra | STRING | no | A closing sentence added to the text, for example: Keep the dog unchanged. | default '' |

Outputs: `STRING`, `STRING`
