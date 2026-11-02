# Audio Fade SY (`SYAudioFade`)

Source: `nodes/sy_audio_fade.py`

**What it does:** Fades a sound in at the start and out at the end. Pick a straight, smooth or fast-rising curve. If the two fades would overlap they shrink in proportion.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to fade. |  |
| fade_in_seconds | FLOAT | yes | How long the sound takes to rise from silence. 0 = no fade in. | 0.0 to 60.0, step 0.01, default 0.5 |
| fade_out_seconds | FLOAT | yes | How long the sound takes to sink to silence at the end. 0 = no fade out. | 0.0 to 60.0, step 0.01, default 0.5 |
| curve | COMBO | yes | Shape of the fade. Smooth eases at both ends; exponential rises slowly then quickly. | one of: linear, smooth, exponential |

Outputs: `AUDIO`

## How to use

1. Connect a sound to **audio**.
2. Set **fade_in_seconds** and **fade_out_seconds**. Use 0 to skip one of them.
3. Pick the **curve**: smooth is a good default.
4. The output **AUDIO** is a new sound with the same length and sample rate. The original is not changed.
