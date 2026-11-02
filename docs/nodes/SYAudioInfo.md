# Audio Info SY (`SYAudioInfo`)

Source: `nodes/sy_audio_info.py`

**What it does:** Reads facts about a sound: length in seconds, sample rate, channels, number of samples, loudest peak and average loudness in dB. A silent sound reports -120 dB.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to measure. |  |

Outputs: `FLOAT`, `INT`, `INT`, `INT`, `FLOAT`, `FLOAT`, `STRING`

## How to use

1. Connect a sound to **audio**.
2. Wire the single numbers wherever you need them, or show **report** in a text preview.
3. Peak near 0 dB means the sound is at full scale and may clip if you make it louder.
