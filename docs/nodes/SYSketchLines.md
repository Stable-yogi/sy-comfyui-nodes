# SketchLines SY (`SYSketchLines`)

Source: `nodes/sy_sketch_lines.py`

**What it does:** Turns a photo into a clean pen drawing: black lines on white paper. Compares a fine and a wide blur of the picture and keeps the edges. Turn invert on for white lines on black.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| image | IMAGE | yes | The photo to turn into a line drawing. | picture batch [B,H,W,3] |
| detail | FLOAT | yes | Width of the fine blur in pixels. Bigger gives fewer, thicker lines. | 0.3 to 4.0, step 0.05, default 1.0 |
| sharpness | FLOAT | yes | How strongly the two blurs are compared. Higher picks out more edges. | 1.0 to 50.0, step 0.5, default 20.0 |
| cutoff | FLOAT | yes | Edge strength below this level becomes line. Raise it for more lines. | 0.0 to 1.0, step 0.01, default 0.5 |
| softness | FLOAT | yes | How hard the edge between line and paper is. Higher is crisper. | 1.0 to 100.0, step 0.5, default 30.0 |
| invert | BOOLEAN | yes | On gives white lines on black. Off gives black lines on white paper. | default False |

Outputs: `IMAGE`

## How to use

1. Connect a photo to image.
2. Start with the defaults. Raise cutoff for more lines, or lower detail for finer lines.
3. sharpness picks out more edges when higher, and softness makes the line edge harder when higher.
4. Turn invert on for white lines on black.
Output: a line drawing, black lines on white paper.
