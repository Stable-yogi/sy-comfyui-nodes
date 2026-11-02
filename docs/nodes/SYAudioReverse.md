# Audio Reverse SY (`SYAudioReverse`)

Source: `nodes/sy_audio_reverse.py`

**What it does:** Plays a sound backwards. The length and sample rate stay the same.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to turn around. |  |

Outputs: `AUDIO`

## How to use

1. Connect a sound to **audio**.
2. The output **AUDIO** is the same sound played from the end to the start.
