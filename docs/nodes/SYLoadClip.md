# Load Clip SY (`SYLoadClip`)

Source: `nodes/sy_load_clip.py`

**What it does:** Loads a video or a sound file from the input folder and trims it: start time, length and a frame limit. It shows the frame count, fps and length so you do not have to guess, and cuts the sound to match the frames.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| video | COMBO | yes | A video from the input folder. You can also upload one. (none) = load only a sound. | one of: (none) |
| sound | COMBO | yes | A sound file from the input folder. Only used when video is (none). | one of: (none) |
| start_seconds | FLOAT | yes | Where to start, in seconds from the beginning. | 0.0 to 100000.0, step 0.1, default 0.0 |
| length_seconds | FLOAT | yes | How many seconds to keep. 0 = to the end. | 0.0 to 100000.0, step 0.1, default 0.0 |
| max_frames | INT | yes | Frame limit after trimming. 0 = no limit. | 0 to 100000, default 0 |

Outputs: `IMAGE`, `AUDIO`, `FLOAT`, `INT`, `FLOAT`, `STRING`
