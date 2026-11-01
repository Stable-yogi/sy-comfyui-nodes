# MultiRefLabel SY (`SYMultiRefLabel`)

Source: `nodes/sy_multi_ref_label.py`

**What it does:** Labels your reference pictures as 'Image 1', 'Image 2' and so on, then adds the task. Use it when an edit model gets several pictures. Can put the task first, renumber the pictures without gaps, and warns when the task names a picture you did not describe.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| task | STRING | yes | What the model should do, using the names Image 1, Image 2 and so on. | default '', multiline |
| ref_1 | STRING | no | Short description of the first picture. Leave empty if unused. | default '' |
| ref_2 | STRING | no | Short description of the second picture. Leave empty if unused. | default '' |
| ref_3 | STRING | no | Short description of the third picture. Leave empty if unused. | default '' |
| ref_4 | STRING | no | Short description of the fourth picture. Leave empty if unused. | default '' |
| label | STRING | no | The word used before each number, for example Image or Picture. | default 'Image' |
| task_first | BOOLEAN | no | On: write the task before the list of pictures. | default False |
| renumber | BOOLEAN | no | On: number the filled slots 1, 2, 3 with no gaps. | default False |

Outputs: `STRING`, `INT`, `STRING`

## How to use

1. In ref_1 to ref_4, write a short description of each reference picture. Leave unused slots empty.
2. In task, say what the model should do, using the names Image 1, Image 2 and so on.
3. Optional: change label (the word before each number), turn task_first on to put the task before the list, and renumber on to number the filled slots without gaps.
Outputs: the finished prompt, the count of pictures and an info line. It warns when the task names a picture you did not describe.
