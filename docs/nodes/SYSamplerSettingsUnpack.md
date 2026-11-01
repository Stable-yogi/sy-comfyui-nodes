# Sampler Settings Unpack SY (`SYSamplerSettingsUnpack`)

Source: `nodes/sy_sampler_settings.py`

**What it does:** Splits a sampler settings bundle back into steps, cfg, sampler, scheduler and denoise. Bundles made before denoise existed give denoise 1.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| settings | SY_SAMPLER_SETTINGS | yes | The bundle from a Sampler Settings node. |  |

Outputs: `INT`, `FLOAT`, `STRING`, `STRING`, `FLOAT`, `STRING`

## How to use

1. Connect the settings output of Sampler Settings SY to the settings input.
2. Use the outputs steps, cfg, sampler_name, scheduler and denoise where you need them, for example on a sampler node.
3. A bundle made before denoise existed gives denoise 1. The info output shows the values in one line.
