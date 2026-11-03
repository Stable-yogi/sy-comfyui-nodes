# Overlap Blend SY (`SYOverlapBlend`)

Source: `nodes/sy_overlap_blend.py`

**What it does:** Joins two clips with a smooth cross-fade over the frames they share, so the seam does not jump. The last frames of clip A fade into the first frames of clip B.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| clip_a | IMAGE | yes | The first clip. Its last frames fade out. | picture batch [B,H,W,3] |
| clip_b | IMAGE | yes | The second clip. Its first frames fade in. Must be the same size as clip_a. | picture batch [B,H,W,3] |
| overlap_frames | INT | yes | How many frames the two clips share and cross-fade over. | 1 to 1000, default 5 |
| curve | COMBO | yes | How fast clip B takes over during the shared frames. | one of: linear, smooth, ease in, ease out |

Outputs: `IMAGE`, `INT`

## How to use

1. Connect the first clip to **clip_a** and the second to **clip_b**. Both must have the same width, height and colour channels.
2. Set **overlap_frames** to how many frames they share. It cannot be longer than either clip.
3. Pick the **curve**: smooth is a gentle S shape, ease in starts slowly, ease out starts fast.
4. The output **joined** is the full clip. **frames_out** tells you its length.
