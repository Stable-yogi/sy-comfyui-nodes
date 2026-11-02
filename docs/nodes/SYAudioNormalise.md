# Audio Normalise SY (`SYAudioNormalise`)

Source: `nodes/sy_audio_normalise.py`

**What it does:** Makes a sound louder or quieter so its loudest point (peak) or its average loudness (RMS) hits a target. Silent sound is left alone. Nothing is ever pushed past full scale.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to adjust. |  |
| target_db | FLOAT | yes | Level to reach in dB. 0 is the loudest possible; -1 leaves a little room. | -60.0 to 0.0, step 0.1, default -1.0 |
| mode | COMBO | yes | Peak aims the loudest moment at the target. Average (RMS) aims the overall loudness. | one of: peak, average (RMS) |
| max_gain_db | FLOAT | yes | Most the sound may be made louder, so quiet hiss is not blown up. | 0.0 to 60.0, step 0.5, default 30.0 |

Outputs: `AUDIO`, `FLOAT`

## How to use

1. Connect a sound to **audio**.
2. Set **target_db**: -1 is a safe choice for the final sound.
3. Pick **mode**: peak for safe maximum level, average (RMS) for even loudness between clips. In RMS mode loud spikes are limited at full scale.
4. Keep **max_gain_db** low if the sound has hiss you do not want raised.
5. The output **AUDIO** is the adjusted sound and **gain_db** tells you how much was applied.
