# Audio Loop To Length SY (`SYAudioLoopToLength`)

Source: `nodes/sy_audio_loop_to_length.py`

**What it does:** Makes a sound exactly as long as you ask: repeats it with a soft crossfade, optionally fades the end, or simply cuts / pads with silence.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to repeat, cut or pad. |  |
| seconds | FLOAT | yes | Exact length of the result in seconds. | 0.1 to 3600.0, step 0.1, default 10.0 |
| crossfade_seconds | FLOAT | yes | Overlap blended at each loop join. Limited to half the clip. | 0.0 to 5.0, step 0.01, default 0.05 |
| mode | COMBO | yes | Loop repeats the sound. Loop then fade out closes with a 1 s fade. The last cuts or pads with silence. | one of: loop, loop then fade out, cut or pad with silence |

Outputs: `AUDIO`

## How to use

1. Connect a sound to **audio**.
2. Set **seconds** to the length you need.
3. Pick **mode**: loop to repeat, loop then fade out for an ending, or cut or pad with silence for no repeating.
4. Raise **crossfade_seconds** if you hear a click at the joins.
5. The output **AUDIO** has the exact length and the same sample rate.
