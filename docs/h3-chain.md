# H3 chain nodes (SY/Utility)

Source: `nodes/sy_h3_chain.py`, with helpers in `nodes/_sy_h3chain_common.py`, `_sy_h3chain_engine.py`, `_sy_h3chain_session.py` and `_sy_h3chain_video.py`.

Ported from ComfyUI-H3-Continuous by Loop Forge (MIT licence, copy in `third_party/ComfyUI-H3-Continuous/LICENSE`). Changed by Stable Yogi: renamed to the SY standard, sockets renamed, texts rewritten. The maths and the on-disk format are unchanged, so a session written by the original pack can be read by these nodes and the other way round.

## What the five nodes do

Make one long video out of several shots without a visible cut. Each shot after the first opens on an exact replay of the end of the shot before it. The replayed part is cut off again when the shots are joined.

| Node | Id | Job |
|---|---|---|
| H3 Chain Settings SY | `SYH3ChainSettings` | Models, sampler, canvas size and seed. One node feeds the whole chain. |
| H3 Render Segment SY | `SYH3RenderSegment` | One shot: prompt, references, length. Wire its `chain_state` into the next shot. |
| H3 Chain To Video SY | `SYH3ChainToVideo` | Joins the shots into one video. |
| H3 Repair Segment SY | `SYH3RepairSegment` | Re-renders one shot in place without touching the others. |
| H3 Load Session SY | `SYH3LoadSession` | Picks up a session that is already on disk. |

Sockets: `SY_H3_SETTINGS` (settings) and `SY_H3_CHAIN` (chain state). They only fit each other.

Files go to `output/h3_continuous/<session>/`: `seg_01.mp4`, `seg_01.tail.mp4`, `manifest.json` and the joined file.

Needs a ComfyUI that has MiniMax H3 support (`comfy_extras/nodes_minimax_h3.py`, ComfyUI 0.34.0 or newer). On an older ComfyUI the five nodes do not load and the other SY nodes are not affected. The console shows one line saying why.

## Settings in plain words

**chain_seed.** The seed of the whole chain. Each shot gets its own seed from it. It is not called `seed` on purpose: ComfyUI would add a "randomise" control to a widget with that name and the whole chain would re-render on every run. A shot can also have its own seed in `seed_override` (0 means use the chain seed).

**session_name.** The folder name under `output/h3_continuous/`. The first shot reads it, later shots inherit it from `chain_state`. The repair node has its own `session_name`.

**ref_image_size.** `match` scales reference pictures to the video size. `max` uses a 2048 pixel short edge for the best likeness and is several times slower.

**handoff_mode.**
- `latent` (default). The end of the last shot is cut straight out of that shot's own latent and pinned as the opening of the next one. No VAE is used, so the anchor is exact and one encode per shot is saved.
- `pixel`. The end is decoded, written as an mp4, read back and encoded again. It is slower and loses a little, but it is the only mode that survives a change of picture size part way through, and the only one that can resume a session made before latent endings existed.

Both forms are always written to disk, so a session can be resumed in either mode. If a session has no latent ending, `latent` falls back to `pixel` by itself and says so in the console.

**drift_arrest.** In a long chain, colour and brightness slowly wander because each shot only continues the last one. This pulls every handoff back toward shot 1 by the given fraction of the measured error. 0 is off, 0.4 to 0.6 is the useful range. It is a fraction and not a reset, so no step shows at the joins. Large corrections are capped so a real lighting change is not fought. It needs `handoff_mode` `latent`. Changing it re-renders every shot after the first.

**stabilize** (on H3 Chain To Video). Flattens the slow drift of the finished cut away from its own opening. 0 is off, 0.7 to 1.0 is the useful range. The per-frame mean of each colour channel is smoothed over two seconds and a gain aimed at shot 1's level is applied. Black stays black, the curve is smooth, and gains are limited to plus or minus 25 percent. It costs one extra decoding pass and no GPU. It fixes colour only. For likeness drift use `drift_arrest`.

**crf** (on H3 Chain To Video). Quality of the joined file. Lower is better and bigger, 0 is lossless.

## Settings of one shot

**prompt.** The clip carried in from the previous shot gets no tag; it never reaches the text encoder. Describe it in plain words, for example "the shot opens on an exact replay of the preceding shot and carries straight on". Nothing new can be scheduled inside the replayed opening.

**seconds.** Length of the shot. It is rounded up to the next length the model can make: 5, 22, 39, 56 ... frames (steps of 17 frames, plus 5). The best range is about 5 to 15 seconds at 24 frames a second.

**handoff_seconds.** How much of the end is replayed in the next shot. It is rounded down to 5, 22, 39 or 56 frames (0.21, 0.92, 1.63 or 2.33 seconds). 39 frames is the sweet spot. Keep it near a fifth of the shot: 1.63 seconds in an 8 second shot joins cleanly, in a 5 second shot the seams get worse. A longer handoff also costs that much new footage per shot. On the last shot set it to 0. It must be shorter than the shot itself, or the node stops with a plain message.

**model** (optional). Replaces the settings model for this shot only. Put a per-shot LoRA here and keep the speed LoRA the chain relies on in the stack you wire in. Changing the LoRA or its strength re-renders this shot and every shot after it.

**resume.** Reuse this shot if it is already in the session with the same settings. Editing an earlier shot still re-renders this one, because each fingerprint includes the shot before it.

**unload_models_after.** Only for the one shot where you run out of memory. It forces a full model reload.

**Reference slots** (`images`, `videos`, `video_audios`, `audios`). These grow as you connect them. Numbers pair a reference video with its own soundtrack (`video_1` goes with `video_audio_1`).

## Repairing one shot

Normally re-rendering shot N changes its ending, so every later shot has to be re-rendered too. H3 Repair Segment SY pins both ends: the opening to the previous shot's handoff clip, and the ending to the clip the next shot already opens on. Nothing after it moves.

`segment_number` starts at 1 and matches `seg_NN.mp4`. The old file is kept as `seg_NN.replaced.mp4`. Turn `pin_ending` off only for the last shot, or when you mean to re-render everything after it.

## Extending a finished session

H3 Load Session SY reads the session from disk with no rendering. Its `chain` output goes into H3 Chain To Video SY, into H3 Repair Segment SY, or into the `chain_state` of another H3 Render Segment SY to add more shots at the end.

## Messages you may see

All errors are plain-word messages (ValueError). A missing or damaged session, a handoff longer than its shot, a ComfyUI that is too old, or a manifest entry that points outside the session folder each stop the node with a sentence saying what to fix.
