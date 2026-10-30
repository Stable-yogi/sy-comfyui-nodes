# EditStepsList SY (`SYEditStepsList`)

Source: `nodes/sy_edit_steps_list.py`

**What it does:** Joins up to five edit steps into one list for an image edit model. Empty steps are skipped and the order is kept.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| style | COMBO | yes | How to write the list: numbers, bullets, or First, Then, Finally. | one of: numbered, bullets, then_words |
| step_1 | STRING | no | Edit step number 1. Leave empty to skip it. | default '' |
| step_2 | STRING | no | Edit step number 2. Leave empty to skip it. | default '' |
| step_3 | STRING | no | Edit step number 3. Leave empty to skip it. | default '' |
| step_4 | STRING | no | Edit step number 4. Leave empty to skip it. | default '' |
| step_5 | STRING | no | Edit step number 5. Leave empty to skip it. | default '' |

Outputs: `STRING`
