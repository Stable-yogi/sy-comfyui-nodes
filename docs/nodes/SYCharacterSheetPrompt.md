# CharacterSheetPrompt SY (`SYCharacterSheetPrompt`)

Source: `nodes/sy_character_sheet_prompt.py`

**What it does:** Writes a prompt that asks for a character reference sheet with the views you pick, with the same face and outfit in each view.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| character | STRING | yes | Describe the character: looks, clothes, age, anything that must stay the same. | default '', multiline |
| front | BOOLEAN | yes | Include a front view. | default True |
| side | BOOLEAN | yes | Include a side view. | default True |
| back | BOOLEAN | yes | Include a back view. | default True |
| three_quarter | BOOLEAN | yes | Include a three-quarter view. | default False |
| face_close_up | BOOLEAN | yes | Include a close-up of the face. | default False |
| full_body | BOOLEAN | yes | Include a full-body shot. | default False |
| background | COMBO | yes | The background behind the character. | one of: plain_white, plain_grey, transparent_look, none |
| layout | COMBO | yes | Put the views in a grid or in one row. | one of: grid, row |

Outputs: `STRING`
