# Save Result SY (`SYSaveResult`)

Source: `nodes/sy_save_result.py`

**What it does:** Saves a picture, video or sound. Files go into a folder named after your project and the date, the settings text is saved beside each file, and the saved path is shown in the node.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| project | STRING | yes | Folder name for this project, inside the ComfyUI output folder. | default 'SY' |
| name | STRING | yes | Start of the file name. A counter is added. | default 'result' |
| folder_by_date | BOOLEAN | yes | On: a folder per day inside the project folder. | default True |
| image_format | COMBO | yes | File type for pictures. png keeps the workflow inside the file. | one of: png, jpg, webp |
| quality | INT | yes | Quality for jpg and webp. png ignores it. | 1 to 100, default 95 |
| image | IMAGE | no | Pictures or frames to save as picture files. | picture batch [B,H,W,3] |
| video | VIDEO | no | A video to save as mp4. |  |
| audio | AUDIO | no | Sound to save as flac. |  |
| settings | STRING | no | Settings text (for example from Sampler SY). Saved as a .txt beside each file. | default '' |

Outputs: `STRING`

## How to use

1. Connect an image, a video or an audio to the matching input. Any of the three can be used.
2. Set project (the folder name) and name (the start of the file name). A counter is added. Turn folder_by_date on for a folder per day.
3. Pick image_format and quality. Pictures save as png, jpg or webp, video as mp4, sound as flac.
4. Connect settings text to get a .txt beside each file. The saved path comes out on saved_path.
