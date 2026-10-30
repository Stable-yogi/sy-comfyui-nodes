# VoiceLengthEstimate SY (`SYVoiceLengthEstimate`)

Source: `nodes/sy_voice_length_estimate.py`

**What it does:** Guesses how long a spoken line takes and gives a matching video frame count. It is an estimate, not a measurement.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The line the voice will say. Speech tags like <d> are ignored. | default '', multiline |
| mode | COMBO | yes | Count words or characters. Change the speed too when you switch. | one of: words, characters |
| speed | INT | yes | Words per minute in words mode, characters per minute in characters mode. | 40 to 400, default 150 |
| pause_per_sentence | FLOAT | yes | Seconds of pause added after each sentence. | 0.0 to 3.0, step 0.05, default 0.3 |
| extra_seconds | FLOAT | yes | Spare seconds added at the end. | 0.0 to 30.0, step 0.1, default 0.5 |
| fps | INT | yes | Frames per second of the video. | 1 to 120, default 24 |
| snap_step | INT | yes | Frames grow in jumps of this size. Step 16 + offset 1 gives 17, 33, 49. Step 17 + offset 5 gives 5, 22, 39. | 1 to 64, default 16 |
| snap_offset | INT | yes | Frames are step times a whole number, plus this offset. Use 5 with step 17 for the video model. | 0 to 64, default 1 |

Outputs: `FLOAT`, `INT`, `STRING`
