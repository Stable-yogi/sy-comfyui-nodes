# Audio Beat Finder SY (`SYAudioBeatFinder`)

Source: `nodes/sy_audio_beat_finder.py`

**What it does:** Finds loud hits in a sound, such as drum beats, and lists their times in seconds and as video frame numbers. Stereo is mixed to mono first. A hit in the very first window is counted.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| audio | AUDIO | yes | The sound to search for beats. |  |
| sensitivity | FLOAT | yes | Higher finds more, weaker beats. Lower finds only the strongest hits. | 0.0 to 1.0, step 0.01, default 0.5 |
| min_gap_seconds | FLOAT | yes | Beats closer together than this are counted once. | 0.05 to 5.0, step 0.01, default 0.25 |
| window_ms | INT | yes | Size of each listening slice in milliseconds. Smaller is more exact in time. | 5 to 200, step 1, default 20 |
| max_beats | INT | yes | Stop after this many beats. | 1 to 10000, step 1, default 1000 |
| fps | FLOAT | yes | Frames per second of your video. Used to turn beat times into frame numbers. | 1.0 to 240.0, step 0.01, default 24.0 |

Outputs: `STRING`, `STRING`, `INT`

## How to use

1. Connect the sound to **audio**.
2. Set **fps** to the frame rate of your video.
3. Raise **sensitivity** if beats are missed, lower it if too many are found.
4. Raise **min_gap_seconds** to ignore quick double hits.
5. Use **beat_times** or **beat_frames** to cut or flash your video on the beat.

How it decides: each window is compared with the average loudness around it (one second to each side). A window is a beat when it is a local peak and louder than that average times (1 + (1 - sensitivity) x 4).
