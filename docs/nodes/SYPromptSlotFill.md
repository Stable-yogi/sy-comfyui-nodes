# Prompt Slot Fill SY (`SYPromptSlotFill`)

Source: `nodes/sy_prompt_slot_fill.py`

**What it does:** Fills named slots like [subject] or [place] in a template from up to six text inputs. Empty slots disappear together with their stray comma.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| template | STRING | yes | Prompt with slots in square brackets, like [subject]. | default '[subject], [place], [light], [style]', multiline |
| slot_1_name | STRING | yes | Slot 1 name. It matches [name] in the template. | default 'subject' |
| slot_2_name | STRING | yes | Slot 2 name. It matches [name] in the template. | default 'place' |
| slot_3_name | STRING | yes | Slot 3 name. It matches [name] in the template. | default 'light' |
| slot_4_name | STRING | yes | Slot 4 name. It matches [name] in the template. | default 'style' |
| slot_5_name | STRING | yes | Slot 5 name. It matches [name] in the template. | default 'mood' |
| slot_6_name | STRING | yes | Slot 6 name. It matches [name] in the template. | default 'extra' |
| slot_1 | STRING | no | Text for slot 1. Leave empty to drop the slot. | default '', multiline |
| slot_2 | STRING | no | Text for slot 2. Leave empty to drop the slot. | default '', multiline |
| slot_3 | STRING | no | Text for slot 3. Leave empty to drop the slot. | default '', multiline |
| slot_4 | STRING | no | Text for slot 4. Leave empty to drop the slot. | default '', multiline |
| slot_5 | STRING | no | Text for slot 5. Leave empty to drop the slot. | default '', multiline |
| slot_6 | STRING | no | Text for slot 6. Leave empty to drop the slot. | default '', multiline |

Outputs: `STRING`, `STRING`

## How to use

1. Write a **template** with names in square brackets, for example [subject], [place], [light], [style].
2. Check that each **slot_1_name** to **slot_6_name** matches a name in the template. Every name must be different.
3. Type the words in **slot_1** to **slot_6**, for example **slot_1** = a red fox. Leave a slot empty to drop it and its comma.
4. Use the **text** output as your finished prompt. The **unused** output lists template slots that had no text.
