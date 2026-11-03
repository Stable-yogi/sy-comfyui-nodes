# MOSS Speed Up SY (`SYMossSpeedUp`)

Source: `nodes/sy_moss_speed_up.py`

**What it does:** Makes MOSS-Image pictures faster. On some steps the big network is skipped and its result is predicted from the steps before. mild changes the picture very little, strong is faster but can change small details like letters. Works with every sampler, er_sde included.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | A MOSS-Image model (ComfyUI 0.43 or newer). |  |
| preset | COMBO | yes | off = normal speed. mild skips about 3 in 10 steps, middle about 4, strong about 5. manual uses the four numbers below. | one of: off, mild, middle, strong, manual |
| warmup_steps | INT | yes | manual only. The first steps always run: they set the shape of the picture. | 2 to 200, default 8 |
| window | FLOAT | yes | manual only. After the warm-up one step in this many runs. 2 = every other step. | 1.0 to 8.0, step 0.25, default 2.0 |
| window_growth | FLOAT | yes | manual only. The window grows by this after each run, so later steps skip more. | 0.0 to 4.0, step 0.05, default 0.25 |
| tail_steps | INT | yes | manual only. The last steps always run: they draw the fine detail. | 1 to 50, default 2 |
| curve_degree | INT | no | How bendy the prediction curve is. 4 works for most pictures. | 1 to 8, default 4 |
| smoothing | FLOAT | no | Higher = a calmer, more careful prediction. | 0.001 to 10.0, step 0.01, default 0.1 |
| history | INT | no | How many past real steps the prediction looks at. | 2 to 32, default 8 |

Outputs: `MODEL`, `STRING`

## How to use

1. Put the node between the model loader and the sampler: model loader -> **MOSS Speed Up SY** -> KSampler (or Sampler SY).
2. Pick a **preset**. Start with **mild**: at 25 steps it skips 8 steps. **middle** skips 10, **strong** skips 13. **off** gives the normal picture.
3. Connect **plan** to a text preview to see, before you run, how many steps each preset skips at 20, 25, 30 and 50 steps. R = the model runs, . = skipped.
4. Run. After the run the node shows a **last run** line, for example "25 steps: 8 skipped, 17 ran. Model calls: 16 of 50 skipped (32% fewer)." The same line is printed in the ComfyUI console.
5. For posters and signs with words, stay on **mild**: stronger presets change small details more.
6. **manual**: set **warmup_steps**, **window**, **window_growth** and **tail_steps** yourself. Warm-up below 2, window below 1 or tail below 1 is refused.

The speed-up is only on the model steps; loading, text encoding and decoding take the same time as before. Without the node, or on **off**, the model is not changed at all.
