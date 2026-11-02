# Audio High Low Pass SY (`SYAudioHighLowPass`)

Source: `nodes/sy_audio_high_low_pass.py`

**What it does:** Removes low rumble (high-pass) or high hiss (low-pass). Pick the cutoff frequency and how steep the cut is. The sound keeps its length and sample rate.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to filter. |  |
| mode | COMBO | yes | High-pass removes the low sounds below the cutoff. Low-pass removes the high sounds above it. | one of: high-pass (cut lows), low-pass (cut highs) |
| cutoff_hz | FLOAT | yes | The pitch where the cut starts, in Hz. At this pitch the sound is about 30 percent quieter. | 20.0 to 20000.0, step 1.0, default 120.0 |
| slope | COMBO | yes | How sharply the cut bites. Steeper cuts leave less of the unwanted sound. | one of: gentle (6 dB), normal (12 dB), steep (24 dB) |

Outputs: `AUDIO`

## How to use

1. Connect a sound to **audio**.
2. For rumble or wind, pick high-pass with a cutoff around 80 to 150 Hz. For hiss, pick low-pass with a cutoff around 8000 Hz.
3. Pick the **slope**. Normal is a good start.
4. The cutoff must stay below half the sound's sample rate (22050 Hz for 44100 Hz audio); otherwise the node stops with a message.
