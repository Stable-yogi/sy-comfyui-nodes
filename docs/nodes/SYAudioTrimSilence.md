# Audio Trim Silence SY (`SYAudioTrimSilence`)

Source: `nodes/sy_audio_trim_silence.py`

**What it does:** Cuts quiet stretches off the start and/or end of a sound, keeping a little padding. Tells you how many seconds were removed. All-silent sound keeps a short piece from the start.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to trim. |  |
| threshold_db | FLOAT | yes | Anything quieter than this counts as silence. Higher (like -30) trims more. | -90.0 to -10.0, step 1.0, default -50.0 |
| pad_seconds | FLOAT | yes | Silence to leave around the sound so the edges are not cut hard. | 0.0 to 5.0, step 0.01, default 0.05 |
| trim | COMBO | yes | Cut the silence at the start, at the end, or both. | one of: both, start, end |
| min_keep_seconds | FLOAT | yes | The result is never shorter than this, even if everything is quiet. | 0.01 to 10.0, step 0.01, default 0.1 |

Outputs: `AUDIO`, `FLOAT`

## How to use

1. Connect a sound to **audio**.
2. Set **threshold_db**: -50 trims only near-silence, -30 also trims soft room noise.
3. Choose **trim**: both, start only or end only.
4. Raise **pad_seconds** if the cut sounds too sudden.
5. The output **AUDIO** is the trimmed sound and **trimmed_seconds** says how much was cut.
