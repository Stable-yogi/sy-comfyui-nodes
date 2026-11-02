# Audio Waveform Picture SY (`SYAudioWaveformPicture`)

Source: `nodes/sy_audio_waveform_picture.py`

**What it does:** Draws a sound as a picture: bars, a line or a filled shape in the colour you pick. A silent sound gives a flat line in the middle. Useful for videos and checks.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to draw. |  |
| width | INT | yes | Picture width in pixels. The whole sound is squeezed into it. | 64 to 4096, step 1, default 1024 |
| height | INT | yes | Picture height in pixels. | 32 to 2048, step 1, default 256 |
| style | COMBO | yes | Bars: separate bars. Line: only the outline. Filled: a solid shape. | one of: bars, line, filled |
| wave_colour_r | FLOAT | yes | Red part of the wave colour. 0 = none, 1 = full. | 0.0 to 1.0, step 0.01, default 0.83 |
| wave_colour_g | FLOAT | yes | Green part of the wave colour. 0 = none, 1 = full. | 0.0 to 1.0, step 0.01, default 0.65 |
| wave_colour_b | FLOAT | yes | Blue part of the wave colour. 0 = none, 1 = full. | 0.0 to 1.0, step 0.01, default 0.22 |
| background_grey | FLOAT | yes | Grey level of the background. 0 = black, 1 = white. | 0.0 to 1.0, step 0.01, default 0.1 |
| channels | COMBO | yes | Mixed: one wave for all channels. Each channel: one wave per channel, stacked top to bottom. | one of: mixed, each channel |

Outputs: `IMAGE`

## How to use

1. Connect a sound to **audio**.
2. Set **width** and **height** to the size you need (for a video overlay, use the video size).
3. Pick a **style** and the wave colour. The default is gold on dark grey.
4. Use **each channel** to see left and right separately. The height must allow at least 2 pixels per channel.
