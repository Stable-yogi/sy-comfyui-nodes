# H3 Forecast Speed Up SY (`SYH3ForecastSpeedUp`)

Source: `nodes/sy_h3_forecast_speed_up.py`

**What it does:** Makes MiniMax H3 videos and H3 pictures faster. On some steps the big network is skipped and its result is predicted from the steps before. Use it with 20 or more steps: the 4-step fast mode has nothing to skip. mild changes the result very little, strong is faster but can change small details.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | A MiniMax H3 model (ComfyUI 0.44 or newer). Do not also use H3 Speed Optimizer SY. |  |
| preset | COMBO | yes | off = normal speed. mild skips about 3 in 10 steps, middle about 4, strong about 5. manual uses the four numbers below. | one of: off, mild, middle, strong, manual |
| warmup_steps | INT | yes | manual only. The first steps always run: they set the shape and motion. | 2 to 200, default 6 |
| window | FLOAT | yes | manual only. After the warm-up one step in this many runs. 2 = every other step. | 1.0 to 8.0, step 0.25, default 2.0 |
| window_growth | FLOAT | yes | manual only. The window grows by this after each run, so later steps skip more. | 0.0 to 4.0, step 0.05, default 0.25 |
| tail_steps | INT | yes | manual only. The last steps always run: they draw the fine detail. | 1 to 50, default 2 |
| curve_degree | INT | no | How bendy the prediction curve is. 4 works for most videos. | 1 to 8, default 4 |
| smoothing | FLOAT | no | Higher = a calmer, more careful prediction. | 0.001 to 10.0, step 0.01, default 0.1 |
| history | INT | no | How many past real steps the prediction looks at. Each one keeps a copy of the video rows in memory. | 2 to 32, default 8 |

Outputs: `MODEL`, `STRING`

## How to use

1. Put the node between the model loader and the scheduler and guider: model loader -> **H3 Forecast Speed Up SY** -> BasicScheduler and BasicGuider (both take the model from this node).
2. Use 20 or more steps without the 4-step fast LoRA. With 4 steps every step must run, so nothing is skipped.
3. Pick a **preset**. Start with **mild**. **middle** and **strong** skip more steps. **off** gives the normal video.
4. Connect **plan** to a text preview to see, before you run, how many steps each preset skips at 4, 8, 20 and 30 steps. R = the model runs, . = skipped.
5. Run. After the run the node shows a **last run** line, for example "20 steps: 6 skipped, 14 ran. Model calls: 6 of 20 skipped (30% fewer)." The same line is printed in the ComfyUI console.
6. Use one speed-up node: together with **H3 Speed Optimizer SY** (or a second copy of this node) the run stops with a clear message. ComfyUI's own H3 control nodes work with it. Put this node after the control node: then the control is skipped on the skipped steps too, which is faster.
7. **manual**: set **warmup_steps**, **window**, **window_growth** and **tail_steps** yourself. Warm-up below 2, window below 1 or tail below 1 is refused.

Works for videos and for H3 pictures (length 5). The speed-up is only on the model steps; loading, text encoding and decoding take the same time as before. Without the node, or on **off**, the model is not changed at all.
