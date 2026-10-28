# Sampler Settings Unpack SY (`SYSamplerSettingsUnpack`)

Source: `nodes/sy_sampler_settings.py`

**What it does:** Splits a sampler settings bundle back into steps, cfg, sampler and scheduler.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| settings | SY_SAMPLER_SETTINGS | yes | The bundle from a Sampler Settings node. |  |

Outputs: `INT`, `FLOAT`, `STRING`, `STRING`

## How it was tested

This node was not run by the harness. Reason: run by hand in a real graph on the processor (2026-10-28): Sampler Settings SY then Unpack gave 3 (int), 6.5 (float), euler, normal (text); a real KSampler ran 3 steps with them, the image decoded with finite values, and a settings object missing fields was refused in plain words.


## Verdict

Not run. run by hand in a real graph on the processor (2026-10-28): Sampler Settings SY then Unpack gave 3 (int), 6.5 (float), euler, normal (text); a real KSampler ran 3 steps with them, the image decoded with finite values, and a settings object missing fields was refused in plain words.
