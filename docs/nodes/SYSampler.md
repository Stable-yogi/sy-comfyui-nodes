# Sampler SY (`SYSampler`)

Source: `nodes/sy_sampler.py`

**What it does:** The whole sampling job in one box: noise, steps, guider and sampler. A Fast switch swaps to a short step count. It also gives you the settings it used as text.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The model to sample with. |  |
| positive | CONDITIONING | yes | What you want in the result (your encoded prompt). |  |
| latent | LATENT | yes | The starting latent: an empty one, or one from a picture or clip. |  |
| seed | INT | yes | Same seed and settings give the same result. | 0 to 18446744073709551615, default 0 |
| fast_mode | BOOLEAN | yes | On: use fast_steps. Off: use steps. | default False |
| steps | INT | yes | Steps used when fast mode is off. | 1 to 1000, default 20 |
| fast_steps | INT | yes | Steps used when fast mode is on. | 1 to 1000, default 4 |
| cfg | FLOAT | yes | How strongly to follow the prompt. 1 skips the negative prompt. | 0.0 to 100.0, step 0.1, default 1.0 |
| sampler | COMBO | yes | The sampling method. euler is a safe choice. | one of: euler, euler_ancestral, heun, dpmpp_2m, dpmpp_2m_sde, dpmpp_sde, uni_pc, res_multistep, ddim |
| scheduler | COMBO | yes | How the steps are spread over the noise. | one of: simple, sgm_uniform, karras, exponential, ddim_uniform, beta, normal, linear_quadratic, kl_optimal |
| denoise | FLOAT | yes | 1 makes a new result. Lower keeps part of the start latent. | 0.0 to 1.0, step 0.01, default 1.0 |
| negative | CONDITIONING | no | What you do not want. Used only when cfg is not 1. |  |

Outputs: `LATENT`, `LATENT`, `STRING`, `INT`
