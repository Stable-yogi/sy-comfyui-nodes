# H3LowVRAM SY (`SYH3LowVRAM`)

Source: `nodes/sy_h3_speed.py`

**What it does:** Lowers the peak video memory of the MiniMax H3 model so a size or length that ran out of memory can finish. The default keeps the result identical. Off by default.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | A MiniMax H3 diffusion model. |  |
| enable_low_vram | BOOLEAN | yes | Master switch. Off passes the model through and changes nothing. | default False |
| exact_output | BOOLEAN | no | EXACT keeps your normal result. MAX SAVING also splits attention in head groups; the video may differ. | default True |
| attention_head_groups | INT | no | MAX SAVING only. Split attention into this many head groups. Past 8 gains little. | 1 to 56, default 8 |
| feedforward_chunks | INT | no | Split the feedforward step into this many parts. Same result, less memory. 1 turns it off. | 1 to 64, default 4 |
| min_tokens | INT | no | Split only when the sequence is longer than this. Short ones gain nothing. | 256 to 1048576, step 256, default 4096 |

Outputs: `MODEL`
