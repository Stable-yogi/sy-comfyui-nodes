# MultiRefLabel SY (`SYMultiRefLabel`)

Source: `nodes/sy_multi_ref_label.py`

**What it does:** Labels your reference pictures as 'Image 1', 'Image 2' and so on, then adds the task. Use it when an edit model gets several pictures.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| task | STRING | yes | What the model should do, using the names Image 1, Image 2 and so on. | default '', multiline |
| ref_1 | STRING | no | Short description of the first picture. Leave empty if unused. | default '' |
| ref_2 | STRING | no | Short description of the second picture. Leave empty if unused. | default '' |
| ref_3 | STRING | no | Short description of the third picture. Leave empty if unused. | default '' |
| ref_4 | STRING | no | Short description of the fourth picture. Leave empty if unused. | default '' |

Outputs: `STRING`, `INT`
