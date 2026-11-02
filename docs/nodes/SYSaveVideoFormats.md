# Save Video Formats SY (`SYSaveVideoFormats`)

Source: `nodes/sy_save_video_formats.py`

**What it does:** Saves a batch of frames as an mp4 (h264), webm (vp9), gif or animated webp in the output folder, inside a sy_video subfolder. Never overwrites a file. Audio is used for mp4 and webm only.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The frames to save, in order. | picture batch [B,H,W,3] |
| fps | FLOAT | yes | Frames per second of the saved clip. | 1.0 to 120.0, step 0.01, default 24.0 |
| format | COMBO | yes | File type. mp4 and webm are videos, gif and webp are animated pictures. | one of: mp4_h264, webm_vp9, gif, webp_animated |
| quality | COMBO | yes | Higher quality gives a bigger file. | one of: low, medium, high |
| filename_prefix | STRING | yes | Start of the file name. No slashes or '..'. A number is added. | default 'sy_video' |
| audio | AUDIO | no | Sound for mp4 and webm. It is cut to the length of the video. Ignored for gif and webp. |  |

Outputs: `STRING`

## How to use

1. Connect the frames to **images** and set **fps**.
2. Pick **format**: mp4_h264 or webm_vp9 for videos, gif or webp_animated for short looping pictures. Set **quality**.
3. Optionally connect **audio** (used for mp4 and webm only; it is cut to the video length).
4. The file is written into the output folder under sy_video, and an existing file is never overwritten. The **STRING** output gives the path.
