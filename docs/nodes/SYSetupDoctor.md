# SetupDoctor SY (`SYSetupDoctor`)

Source: `nodes/sy_setup_doctor.py`

**What it does:** Checks this ComfyUI and says each fix in plain words: is ComfyUI Manager there, did every node pack load, which start settings slow it down, which model folders are empty, and which model files sit in the wrong folder. It only reads; it never moves or changes a file.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| check_node_packs | BOOLEAN | yes | Look for node packs that did not load (they make red nodes). | default True |
| check_start_settings | BOOLEAN | yes | Explain start settings such as --lowvram or --cpu that change speed or memory. | default True |
| check_model_places | BOOLEAN | yes | Look for empty model folders and for files in the wrong folder (by name and size). | default True |

Outputs: `STRING`, `STRING`, `INT`
