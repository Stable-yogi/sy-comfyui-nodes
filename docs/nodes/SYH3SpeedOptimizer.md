# H3SpeedOptimizer SY (`SYH3SpeedOptimizer`)

Source: `nodes/sy_h3_speed.py`

**What it does:** Makes MiniMax H3 sampling faster. It skips the rest of the model on steps where the first block barely changed, and can use sparse attention. A switch turns everything off. Other settings that cannot help on your GPU fall back to the normal path.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | A MiniMax H3 diffusion model. |  |
| first_block_cache | BOOLEAN | yes | Skip most blocks when block 0 barely changed since the last step. The main speed-up. | default True |
| fbc_threshold | FLOAT | yes | Total change allowed before a step is computed. 0.08 is near lossless; 0.15-0.20 is faster but softer. | 0.0 to 1.0, step 0.005, default 0.08 |
| fbc_start_percent | FLOAT | yes | Never skip before this fraction of the steps. Early steps set the global structure. | 0.0 to 1.0, step 0.01, default 0.15 |
| fbc_end_percent | FLOAT | yes | Never skip after this fraction of the steps. The last steps set the fine detail. | 0.0 to 1.0, step 0.01, default 0.95 |
| fbc_max_consecutive | INT | yes | Most steps in a row that may be skipped. | 1 to 50, default 3 |
| sparse_attention | COMBO | yes | Sparse attention. auto checks the result and speed on your GPU and keeps the faster way. | one of: auto, enabled, disabled |
| sparse_dense_steps_pct | FLOAT | yes | Fraction of the first steps that always use normal attention. | 0.0 to 1.0, step 0.05, default 0.2 |
| sparse_dense_layers | INT | yes | The first N blocks always use normal attention. | 0 to 50, default 2 |
| sparse_tau | FLOAT | no | Sparse attention threshold. 1.0 is the standard value; higher keeps fewer blocks. | -10.0 to 100.0, step 0.1, default 1.0 |
| sparse_min_video_rows | INT | no | Use sparse attention only when the video part is longer than this. Short ones gain nothing. | 0 to 1000000, default 4096 |
| fbc_cache_device | COMBO | no | Where the saved data lives. cpu saves video memory but is slower. | one of: gpu, cpu |
| verbose | BOOLEAN | no | Write a short summary of skipped steps to the console after each run. | default True |
| enable_speedup | BOOLEAN | no | Master switch. Off passes the model through unchanged and returns False on speedup_enabled. | default True |

Outputs: `MODEL`, `BOOLEAN`
