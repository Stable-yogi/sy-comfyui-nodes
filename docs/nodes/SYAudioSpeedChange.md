# Audio Speed Change SY (`SYAudioSpeedChange`)

Source: `nodes/sy_audio_speed_change.py`

**What it does:** Plays a sound faster or slower. The pitch changes with the speed, like a tape machine. Speed 1 gives back an identical copy.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to speed up or slow down. |  |
| speed | FLOAT | yes | 2 = twice as fast and one octave higher; 0.5 = half speed and lower. 1 = unchanged. | 0.25 to 4.0, step 0.01, default 1.0 |
| method | COMBO | yes | How in-between values are worked out. Cubic is smoother and a little slower. | one of: linear, cubic |

Outputs: `AUDIO`, `FLOAT`

## How to use

1. Connect a sound to **audio**.
2. Set **speed**: above 1 shortens the sound, below 1 stretches it.
3. Pick **method**: linear is fine for most uses, cubic keeps high notes cleaner.
4. Use **seconds** to see the new length, for example to match a video.
