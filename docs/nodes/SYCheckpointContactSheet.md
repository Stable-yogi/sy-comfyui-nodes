# CheckpointContactSheet SY (`SYCheckpointContactSheet`)

Source: `nodes/sy_checkpoint_contact_sheet.py`

**What it does:** Renders the same prompts with several all-in-one checkpoints, one after the other, and gives one labelled sheet: a row per checkpoint, a column per prompt, same seed for all. Each checkpoint is unloaded before the next, so the memory need is that of one checkpoint. Good for picking a model.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| checkpoints | STRING | yes | One checkpoint per line: the file name or a unique part of it. Up to 12. | default '', multiline |
| prompts | STRING | yes | One prompt per line. Up to 6. Each becomes a column. | default 'a portrait photo of a woman in a garden, soft light', multiline |
| negative | STRING | yes | Used for every picture. Empty is fine. | default '', multiline |
| width | INT | yes | Picture width in pixels. | 256 to 2048, step 8, default 1024 |
| height | INT | yes | Picture height in pixels. | 256 to 2048, step 8, default 1024 |
| steps | INT | yes | Same for every checkpoint. | 1 to 150, default 25 |
| cfg | FLOAT | yes | Same for every checkpoint. | 0.0 to 30.0, step 0.1, default 6.0 |
| sampler_name | COMBO | yes | Sampler for every picture. | one of: euler |
| scheduler | COMBO | yes | Scheduler for every picture. | one of: normal |
| seed | INT | yes | Same seed for all, so only the checkpoint changes. | 0 to 18446744073709551615, default 1 |
| label_size | INT | yes | Size of the label text on the sheet. | 10 to 96, default 28 |

Outputs: `IMAGE`, `IMAGE`, `STRING`
