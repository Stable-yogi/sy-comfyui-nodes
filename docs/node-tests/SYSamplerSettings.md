# Sampler Settings SY (`SYSamplerSettings`)

Source: `nodes/sy_sampler_settings.py`

**What it does:** Bundles steps, cfg, sampler and scheduler into one wire so a workflow stays tidy.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| steps | INT | yes | How many denoising steps to run. | 1 to 10000, default 20 |
| cfg | FLOAT | yes | How strongly the prompt is followed. | 0.0 to 100.0, step 0.1, default 5.0 |
| sampler_name | COMBO | yes | The sampling method. | one of: euler, euler_ancestral, heun, dpmpp_2m, dpmpp_2m_sde, dpmpp_sde, uni_pc, res_multistep, ddim |
| scheduler | COMBO | yes | How the noise levels are spaced over the steps. | one of: simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal |

Outputs: `SY_SAMPLER_SETTINGS`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 2 | steps = 1 (min) | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 3 | steps = 10000 (max) | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 4 | steps = 5000 (mid) | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 5 | cfg = 0.0 (min) | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 6 | cfg = 100.0 (max) | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 7 | cfg = 50.0 (mid) | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 8 | sampler_name = 'euler_ancestral' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 9 | sampler_name = 'heun' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 10 | sampler_name = 'dpmpp_2m' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 11 | sampler_name = 'dpmpp_2m_sde' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 12 | sampler_name = 'dpmpp_sde' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 13 | sampler_name = 'uni_pc' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 14 | sampler_name = 'res_multistep' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 15 | sampler_name = 'ddim' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 16 | scheduler = 'sgm_uniform' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 17 | scheduler = 'karras' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 18 | scheduler = 'exponential' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 19 | scheduler = 'ddim_uniform' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 20 | scheduler = 'beta' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 21 | scheduler = 'normal' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 22 | scheduler = 'linear_quadratic' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |
| 23 | scheduler = 'kl_optimal' | PASS | SY_SAMPLER_SETTINGS=dict(steps, cfg, sampler_name, scheduler) |

## Verdict

All 23 cases behaved as expected (23 passed, 0 rejected with a clear message).
