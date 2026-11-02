# Metadata Compare SY (`SYMetadataCompare`)

Source: `nodes/sy_metadata_compare.py`

**What it does:** Compares the saved generation info of two png pictures (prompt, negative prompt, seed, steps, cfg, sampler, scheduler, model, size) and lists what differs. Reads Forge/A1111 and ComfyUI data. Never changes a file.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image_a_path | STRING | yes | First png, a file name or sub path inside the input or output folder. | default '' |
| image_b_path | STRING | yes | Second png, a file name or sub path inside the input or output folder. | default '' |
| only_differences | BOOLEAN | no | On: list only the settings that differ. Off: list every setting. | default True |

Outputs: `STRING`, `BOOLEAN`, `INT`

## How to use

1. Type the file names of two png pictures made by Forge, A1111 or ComfyUI. They are looked up in the ComfyUI input and output folders.
2. Leave **only_differences** on to see just what changed (prompt, seed, steps, cfg, sampler, model, size).
3. Read the **STRING** report. The **BOOLEAN** says if anything differs, the **INT** counts the differences. No file is changed.
