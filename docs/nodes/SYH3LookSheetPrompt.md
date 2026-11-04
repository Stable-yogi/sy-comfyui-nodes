# H3 Look Sheet Prompt SY (`SYH3LookSheetPrompt`)

Source: `nodes/sy_h3_look_sheet_prompt.py`

**What it does:** Writes one video prompt for a character look sheet: hard cuts to a still camera, one framing per shot (face, profile, full body, back, details). Also gives the frame where each shot starts and the shot names, so Best Frames Per Shot SY can pick a still from every shot and Image Grid SY can label them.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| subject | STRING | yes | Who the look sheet is of. Point at the reference picture. | default 'the woman from Picture 1' |
| setting | STRING | yes | Background and light. Plain backgrounds make clean sheets. | default 'a plain light grey studio wall, soft even light' |
| preset | COMBO | yes | Which framings to shoot. custom uses the custom_shots lines. | one of: face set (6), body set (6), full set (12), custom |
| seconds | FLOAT | yes | Clip length. Give each shot about 0.8 s or more. | 1.0 to 30.0, step 0.5, default 10.0 |
| fps | INT | yes | Frames per second of the clip. Sets the shot start frames. | 1 to 60, default 24 |
| custom_shots | STRING | no | One framing per line, for preset custom: a list name like full body front, or your own words. | default '', multiline |
| expression | STRING | no | Optional face expression for every shot, for example calm and neutral. | default '' |

Outputs: `STRING`, `STRING`, `STRING`, `INT`, `STRING`

## How to use

1. Point subject at the reference picture, like "the woman from Picture 1", and pick a preset (face set, body set, full set) or write your own framings in custom_shots.
2. Set seconds and fps to the same values as the video node. Give each shot about 0.8 s or more.
3. Connect prompt to the H3 video node. Keep shot_starts and shot_labels.
4. After the video is made, feed the frames, shot_starts and shot_labels into Best Frames Per Shot SY, then into Image Grid SY for a labelled datasheet.
5. Eye level framings work best; views from far above or below often fail (the notes output warns you).
