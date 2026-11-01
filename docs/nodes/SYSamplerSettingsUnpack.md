# Sampler Settings Unpack SY (`SYSamplerSettingsUnpack`)

Source: `nodes/sy_sampler_settings.py`

**What it does:** Splits a sampler settings bundle back into steps, cfg, sampler, scheduler and denoise. Bundles made before denoise existed give denoise 1.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| settings | SY_SAMPLER_SETTINGS | yes | The bundle from a Sampler Settings node. |  |

Outputs: `INT`, `FLOAT`, `STRING`, `STRING`, `FLOAT`, `STRING`
