# H3 Prompt SY (`SYH3Prompt`)

Source: `nodes/sy_h3_prompt.py`

**What it does:** One box for the video prompt. Builds the text, checks that Picture 1, Picture 2 match the reference pictures you connected, turns seconds into a frame count the model accepts, and checks the time codes against the acting video.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| style | STRING | yes | The look of the clip, for example soft film light. | default '', multiline |
| world | STRING | yes | Where the scene happens and who is in it. | default '', multiline |
| action | STRING | yes | What happens in the clip. Write Picture 1, Picture 2 to point at input pictures. | default '', multiline |
| dialogue | STRING | no | Spoken lines, one per line. Each line gets its own speech tag. | default '', multiline |
| dialogue_language | STRING | no | Language of the spoken lines, for example Japanese. Leave empty for none. | default '' |
| time_codes | STRING | no | One line per moment, like 0-4s: she turns round. | default '', multiline |
| ref_image_1 | IMAGE | no | Reference picture 1. Leave empty if not used. Only its first frame is used. | picture batch [B,H,W,3] |
| ref_image_2 | IMAGE | no | Reference picture 2. Leave empty if not used. Only its first frame is used. | picture batch [B,H,W,3] |
| ref_image_3 | IMAGE | no | Reference picture 3. Leave empty if not used. Only its first frame is used. | picture batch [B,H,W,3] |
| ref_image_4 | IMAGE | no | Reference picture 4. Leave empty if not used. Only its first frame is used. | picture batch [B,H,W,3] |
| acting_video | IMAGE | no | The acting video as frames. Gives the clip length and checks the time codes. | picture batch [B,H,W,3] |
| fps | FLOAT | no | Frames per second of the clip. | 1.0 to 60.0, step 1.0, default 24.0 |
| seconds | FLOAT | no | Clip length. 0 = take it from the acting video, or 5 seconds if none. | 0.0 to 60.0, step 0.1, default 0.0 |
| label_pictures | BOOLEAN | no | Add a 'Picture 1 is ...' line for each note you wrote below. | default True |
| ref_note_1 | STRING | no | What reference picture 1 shows, for example the hero in a red coat. | default '' |
| ref_note_2 | STRING | no | What reference picture 2 shows, for example the hero in a red coat. | default '' |
| ref_note_3 | STRING | no | What reference picture 3 shows, for example the hero in a red coat. | default '' |
| ref_note_4 | STRING | no | What reference picture 4 shows, for example the hero in a red coat. | default '' |

Outputs: `STRING`, `INT`, `IMAGE`, `STRING`

## How to use

1. Fill in style, world and action. In action, write Picture 1, Picture 2 to point at the reference pictures.
2. Connect reference pictures to ref_image_1 to ref_image_4 (only the first frame is used) and describe them in ref_note_1 to ref_note_4. The node checks that the Picture numbers match what you connected.
3. Add dialogue (one spoken line per line), dialogue_language, and time_codes (one line per moment, like 0-4s: she turns round). Connect an acting_video to take the clip length from it and check the time codes.
4. Set seconds and fps. seconds 0 takes the length from the acting video, or 5 seconds if there is none.
5. The prompt text, the frame count, the reference picture and an info line come out.
