# Pick Best References SY (`SYPickBestReferences`)

Source: `nodes/sy_pick_best_references.py`

**What it does:** Takes the stills of a character datasheet (from Best Frames Per Shot SY) and hands out three of them as Picture 1, 2 and 3 for a video model: by name (face, full body, back) or by number. Also writes the sentence that tells the model what each picture shows.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The datasheet stills, one picture per shot. | picture batch [B,H,W,3] |
| wanted | STRING | yes | Up to 3 lines: a word from the shot name, or a still number. Line 1 becomes Picture 1. | default 'face\nfull body\nback', multiline |
| labels | STRING | no | Shot names, one per still (the labels output of Best Frames Per Shot SY). | default '', multiline |
| character | STRING | no | How the sentence names the person, for example the young woman. | default 'the character' |

Outputs: `IMAGE`, `IMAGE`, `IMAGE`, `STRING`, `STRING`

## How to use

1. Connect the images and labels outputs of Best Frames Per Shot SY (after a look sheet video).
2. In wanted, write up to 3 lines: a word from the shot names (face, full body, back) or a still number. Line 1 becomes Picture 1.
3. Wire picture_1, picture_2 and picture_3 into the video model's reference pictures in the same order.
4. Add prompt_line to your prompt (for example with a text join). It tells the model what each picture shows, which keeps the face the same in every shot.
5. Read info: it says which still went where, and warns when a word matched no shot.
