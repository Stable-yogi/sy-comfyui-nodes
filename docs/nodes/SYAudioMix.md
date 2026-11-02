# Audio Mix SY (`SYAudioMix`)

Source: `nodes/sy_audio_mix.py`

**What it does:** Lays sound B over sound A with a volume for each and an optional delay for B. Different sample rates and mono / stereo are matched for you.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio_a | AUDIO | yes | The base sound. Its sample rate is the one used for the result. |  |
| audio_b | AUDIO | yes | The sound laid over A. A different sample rate is resampled to A's rate (linear). |  |
| volume_a | FLOAT | yes | Volume of A. 1 = unchanged, 0 = silent. | 0.0 to 4.0, step 0.01, default 1.0 |
| volume_b | FLOAT | yes | Volume of B. 1 = unchanged, 0 = silent. | 0.0 to 4.0, step 0.01, default 1.0 |
| b_start_seconds | FLOAT | yes | When B begins, counted from the start of A. | 0.0 to 3600.0, step 0.01, default 0.0 |
| length | COMBO | yes | Length of the result: the longest of the two, A's length, or until B ends. | one of: longest, length of A, length of B placed |
| prevent_clipping | BOOLEAN | yes | On: if the mix would pass full scale, turn the whole mix down. Off: hard limit. | default True |

Outputs: `AUDIO`

## How to use

1. Connect the main sound to **audio_a** and the sound to lay over it to **audio_b**.
2. Set **volume_a** and **volume_b**. For music under a voice, use a low value on the music.
3. Set **b_start_seconds** if B should come in later.
4. Pick **length**: longest keeps everything, length of A cuts B where A ends.
5. Leave **prevent_clipping** on so loud mixes are turned down instead of distorted.
6. The output **AUDIO** is the mixed sound at A's sample rate.
