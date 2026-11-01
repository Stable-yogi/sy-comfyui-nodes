# CharacterSheetPrompt SY (`SYCharacterSheetPrompt`)

Source: `nodes/sy_character_sheet_prompt.py`

**What it does:** Writes a prompt that asks for a character reference sheet with the views you pick, with the same face and outfit in each view. Can also ask for a pose and add style notes, and an info line suggests a canvas shape.

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
| pose | COMBO | no | Ask for one pose in every view. A-pose or T-pose help later 3D work. | one of: any, neutral standing, A-pose, T-pose |
| style_notes | STRING | no | Extra wishes, for example: flat colours, clean line art. | default '', multiline |

Outputs: `STRING`, `STRING`
