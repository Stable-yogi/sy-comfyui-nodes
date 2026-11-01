# EditStepsList SY (`SYEditStepsList`)

Source: `nodes/sy_edit_steps_list.py`

**What it does:** Joins up to eight edit steps into one list for an image edit model: numbered, bullets, First/Then/Finally or one line. Empty steps are skipped, the order is kept, a number you already typed is not doubled, and repeats can be dropped. Also gives the step count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| style | COMBO | yes | How to write the list: numbers, bullets, First/Then/Finally, or one line with semicolons. | one of: numbered, bullets, then_words, one_line |
| step_1 | STRING | no | Edit step number 1. Leave empty to skip it. | default '' |
| step_2 | STRING | no | Edit step number 2. Leave empty to skip it. | default '' |
| step_3 | STRING | no | Edit step number 3. Leave empty to skip it. | default '' |
| step_4 | STRING | no | Edit step number 4. Leave empty to skip it. | default '' |
| step_5 | STRING | no | Edit step number 5. Leave empty to skip it. | default '' |
| step_6 | STRING | no | Edit step number 6. Leave empty to skip it. | default '' |
| step_7 | STRING | no | Edit step number 7. Leave empty to skip it. | default '' |
| step_8 | STRING | no | Edit step number 8. Leave empty to skip it. | default '' |
| skip_duplicates | BOOLEAN | no | On: a step written twice is used once (capitals ignored). | default False |

Outputs: `STRING`, `INT`
