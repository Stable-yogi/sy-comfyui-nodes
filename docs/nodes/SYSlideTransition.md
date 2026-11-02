# Slide Transition SY (`SYSlideTransition`)

Source: `nodes/sy_slide_transition.py`

**What it does:** Joins two clips with a push or a wipe instead of a plain crossfade. The result is clip A without its last frames, then the transition, then clip B without its first frames. Clip B is resized to fit clip A. Both clips must be at least as long as the transition.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images_a | IMAGE | yes | The first clip. Its last frames are used by the transition. | picture batch [B,H,W,3] |
| images_b | IMAGE | yes | The second clip. Its first frames are used by the transition. It is resized to fit clip A. | picture batch [B,H,W,3] |
| frames | INT | yes | How many frames the transition takes. Both clips need at least this many. | 2 to 120, default 12 |
| style | COMBO | yes | Push slides both pictures. Wipe reveals the new picture over the old one. | one of: push left, push right, wipe left, wipe right, wipe down, wipe up |
| softness | FLOAT | yes | How soft the edge of a wipe is. 0 is a hard edge. Push ignores this. | 0.0 to 0.5, step 0.01, default 0.05 |

Outputs: `IMAGE`

## How to use

1. Connect the first clip to **images_a** and the second clip to **images_b**.
2. Set **frames** to the length of the transition; both clips need at least that many frames.
3. Pick **style**: push slides both pictures, wipe reveals the new one over the old one.
4. Raise **softness** for a softer wipe edge (push ignores it).
5. The output **images** is clip A, the transition, then clip B, as one clip.
