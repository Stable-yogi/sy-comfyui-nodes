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
