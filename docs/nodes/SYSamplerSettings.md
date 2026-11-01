# Sampler Settings SY (`SYSamplerSettings`)

Source: `nodes/sy_sampler_settings.py`

**What it does:** Bundles steps, cfg, sampler, scheduler and denoise into one wire so a workflow stays tidy. The info output shows the values in one line and warns about common mistakes, such as cfg 0 or too many steps.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| steps | INT | yes | How many denoising steps to run. | 1 to 10000, default 20 |
| cfg | FLOAT | yes | How strongly the prompt is followed. | 0.0 to 100.0, step 0.1, default 5.0 |
| sampler_name | COMBO | yes | The sampling method. | one of: euler, euler_ancestral, heun, dpmpp_2m, dpmpp_2m_sde, dpmpp_sde, uni_pc, res_multistep, ddim |
| scheduler | COMBO | yes | How the noise levels are spaced over the steps. | one of: simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal |
| denoise | FLOAT | no | 1 makes a new picture. Lower keeps part of the input picture, for example 0.6. | 0.0 to 1.0, step 0.01, default 1.0 |

Outputs: `SY_SAMPLER_SETTINGS`, `STRING`

## How to use

1. Set steps, cfg, sampler_name and scheduler. Set denoise to 1 for a new picture, or lower (for example 0.6) to keep part of an input picture.
2. Connect the settings output to a node that takes sampler settings, or to Sampler Settings Unpack SY.
3. Read the info output. It shows all values in one line and warns about mistakes such as cfg 0 or too many steps.
