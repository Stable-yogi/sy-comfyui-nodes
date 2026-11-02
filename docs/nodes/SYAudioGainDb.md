# Audio Gain dB SY (`SYAudioGainDb`)

Source: `nodes/sy_audio_gain_db.py`

**What it does:** Makes a sound louder or quieter in decibels. Peaks above full scale are either cut flat (clamp) or squeezed gently (soft limit). Also tells you the loudest peak of the result.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to change. |  |
| gain_db | FLOAT | yes | Change in loudness. +6 is about twice as loud, -6 about half. 0 = unchanged. | -60.0 to 60.0, step 0.1, default 0.0 |
| limit | COMBO | yes | What happens to peaks above full scale. Clamp cuts them flat; soft limit rounds them off gently. | one of: clamp, soft limit |

Outputs: `AUDIO`, `FLOAT`

## How to use

1. Connect a sound to **audio**.
2. Set **gain_db**: positive for louder, negative for quieter.
3. Pick **limit**: clamp is exact but can sound harsh on big boosts; soft limit leaves everything below half scale untouched and bends louder peaks towards full scale.
4. Read **peak_after_db** to see how close to full scale (0 dB) the result is.
