# H3 Repair Segment SY (`SYH3RepairSegment`)

Source: `nodes/sy_h3_chain.py`

**What it does:** Re-render one segment of a finished session, in place.

Normally re-rendering segment N changes its ending, so every segment after it has to be re-rendered too. This node pins BOTH ends: the opening to the previous segment's handoff clip, and the ending to the very clip the next segment already opens on. Nothing downstream moves.

segment_number is 1-based and matches seg_NN.mp4 in the session folder. The old file is kept as seg_NN.replaced.mp4. pin_ending: turn it off only for the last segment, or when you mean to re-render everything after this one.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| settings | SY_H3_SETTINGS | yes | The bundle from H3 Chain Settings. |  |
| session_name | STRING | yes | Folder name of the session to repair, under output/h3_continuous/. | default 'my_chain' |
| segment_number | INT | yes | Which segment to re-render. 1 is the first, matching seg_01.mp4. | 1 to 32, default 2 |
| prompt | STRING | yes | The H3 prompt. Tags count per type: image_0 is <Picture 1>, video_0 is <Video 1>, audio_0 is <Audio 1>. | default '', multiline |
| seconds | FLOAT | yes | Length of this segment in seconds. It snaps up to H3's frame grid (24 fps). About 5 to 15 s works best. | 0.25 to 15.0, step 0.25, default 8.0 |
| handoff_seconds | FLOAT | yes | Seconds of this ending replayed at the start of the next segment. Use 0 on the last segment. | 0.0 to 4.0, step 0.125, default 1.625 |
| seed_override | INT | yes | 0 uses the chain seed. Any other number re-rolls just this segment. | 0 to 18446744073709551615, default 0 |
| pin_ending | BOOLEAN | yes | Keep the ending the next segment continues from. Turn off only for the last segment. | default True |
| model | MODEL | no | Optional model for this shot only (for example with a LoRA). It replaces the model from the settings. |  |
| images | COMFY_AUTOGROW_V3 | no | Reference images. They become <Picture 1> to <Picture 9> in the prompt. |  |
| videos | COMFY_AUTOGROW_V3 | no | Reference videos (frames at 24 fps, 2 to 15 s). They become <Video 1> to <Video 3>. |  |
| video_audios | COMFY_AUTOGROW_V3 | no | Soundtrack of the reference video with the same number. |  |
| audios | COMFY_AUTOGROW_V3 | no | Separate reference audio. It becomes <Audio 1> to <Audio 3>. |  |

Outputs: `VIDEO`, `SY_H3_CHAIN`, `STRING`
