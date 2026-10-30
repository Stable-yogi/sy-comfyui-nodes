# H3 Render Segment SY (`SYH3RenderSegment`)

Source: `nodes/sy_h3_chain.py`

**What it does:** One shot in a continuous take: a prompt, its references and how long it runs. It renders right here. Chain shots by wiring this node's chain_state output into the next H3 Render Segment's chain_state input. Each shot after the first opens on an exact replay of the end of the one before it, so the cut is invisible.

The video output is ready as soon as THIS segment finishes. The segment is also written to output/h3_continuous/<session>/ and reused on the next run, so a crash, an interrupt or an edited prompt only costs the segments that changed.

resume: reuse this segment if it is already in the session with the same settings. Editing an earlier segment still re-renders this one, because each fingerprint includes the segment before it.

prompt: the clip carried in from the previous segment gets NO tag (it never reaches the text encoder). Describe it in plain words, for example 'the shot opens on an exact replay of the preceding shot and carries straight on'. Nothing new can be scheduled inside the replayed opening.

handoff_seconds: snapped down to 5, 22, 39 or 56 frames (0.21, 0.92, 1.63 or 2.33 s). 39 frames is the sweet spot. Keep it near a fifth of the segment: 1.63 s in an 8 s segment joins cleanly, in a 5 s segment the seams get worse. A longer handoff also costs that much new footage per segment. On the last segment set it to 0.

model: replaces the settings model for this shot only. Put a per-shot LoRA here, and keep the speed LoRA the chain relies on in the stack you wire in. Changing the LoRA or its strength re-renders this segment and every one after it.

chain_state: leave unconnected on the first segment. It also accepts the chain output of H3 Load Session, to add new segments onto a finished session. unload_models_after is only for the one segment where you run out of memory: it forces a full model reload.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| settings | SY_H3_SETTINGS | yes | The bundle from H3 Chain Settings. |  |
| resume | BOOLEAN | yes | Reuse this segment if it is already rendered with the same settings. | default True |
| prompt | STRING | yes | The H3 prompt. Tags count per type: image_0 is <Picture 1>, video_0 is <Video 1>, audio_0 is <Audio 1>. | default '', multiline |
| seconds | FLOAT | yes | Length of this segment in seconds. It snaps up to H3's frame grid (24 fps). About 5 to 15 s works best. | 0.25 to 15.0, step 0.25, default 8.0 |
| handoff_seconds | FLOAT | yes | Seconds of this ending replayed at the start of the next segment. Use 0 on the last segment. | 0.0 to 4.0, step 0.125, default 1.625 |
| seed_override | INT | yes | 0 uses the chain seed. Any other number re-rolls just this segment. | 0 to 18446744073709551615, default 0 |
| unload_models_after | BOOLEAN | yes | Unload the models after this segment. Only for the one segment where you run out of memory. | default False |
| chain_state | SY_H3_CHAIN | no | The previous segment's chain_state. Leave empty on the first segment of a session. |  |
| model | MODEL | no | Optional model for this shot only (for example with a LoRA). It replaces the model from the settings. |  |
| images | COMFY_AUTOGROW_V3 | no | Reference images. They become <Picture 1> to <Picture 9> in the prompt. |  |
| videos | COMFY_AUTOGROW_V3 | no | Reference videos (frames at 24 fps, 2 to 15 s). They become <Video 1> to <Video 3>. |  |
| video_audios | COMFY_AUTOGROW_V3 | no | Soundtrack of the reference video with the same number. |  |
| audios | COMFY_AUTOGROW_V3 | no | Separate reference audio. It becomes <Audio 1> to <Audio 3>. |  |

Outputs: `VIDEO`, `SY_H3_CHAIN`, `STRING`
