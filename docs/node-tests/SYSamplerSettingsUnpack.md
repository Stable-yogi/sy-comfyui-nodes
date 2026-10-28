# Sampler Settings Unpack SY (`SYSamplerSettingsUnpack`)

Source: `nodes/sy_sampler_settings.py`

**What it does:** Splits a sampler settings bundle back into steps, cfg, sampler and scheduler.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| settings | SY_SAMPLER_SETTINGS | yes | The bundle from a Sampler Settings node. |  |

Outputs: `INT`, `FLOAT`, `STRING`, `STRING`

## How it was tested

This node was not run by the harness. Reason: needs the settings object from Sampler Settings SY. Its unit test checks the unpacking; a run inside a full workflow is still open.


## Verdict

Not run. needs the settings object from Sampler Settings SY. Its unit test checks the unpacking; a run inside a full workflow is still open.
