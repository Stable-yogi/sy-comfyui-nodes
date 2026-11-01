# System Info SY (`SYSystemInfo`)

Source: `nodes/sy_system_info.py`

**What it does:** Reports free video memory and free system memory as a short text and numbers. Shows -1 if unknown. Type how much memory your next step needs and it says if there is enough, or stops the run early with a plain message.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| need_vram_gb | FLOAT | no | VRAM the next step needs, for example 12. 0 means do not check. | 0.0 to 1000.0, step 0.5, default 0.0 |
| need_ram_gb | FLOAT | no | System RAM the next step needs, for example 32. 0 means do not check. | 0.0 to 10000.0, step 0.5, default 0.0 |
| stop_if_short | BOOLEAN | no | On: stop the run with a plain message when there is not enough memory. | default False |

Outputs: `STRING`, `INT`, `INT`, `INT`, `INT`, `BOOLEAN`, `STRING`, `STRING`

## How to use

1. Run the node to get a short report of free video memory (VRAM) and free system memory (RAM). A value of -1 means unknown.
2. Optional: set need_vram_gb and need_ram_gb to what your next step needs (0 means no check). The enough and check outputs say if it fits.
3. Turn on stop_if_short to stop the run with a plain message when memory is short.
