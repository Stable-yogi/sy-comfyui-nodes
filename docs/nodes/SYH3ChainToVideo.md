# H3 Chain To Video SY (`SYH3ChainToVideo`)

Source: `nodes/sy_h3_chain.py`

**What it does:** Joins a session's segments into one cut and drops each segment's replayed opening, so the motion does not stutter once per join.

crf is the quality of the joined file (lower is better and bigger, 0 is lossless).

stabilize flattens the slow drift of the finished cut away from its own opening (0 is off, 0.7 to 1.0 is the useful range). Each colour channel's per-frame mean is smoothed over two seconds, and a gain aimed at segment 1's level is applied. Gains keep black black, and the curve is smooth, so no step shows at a join. Gains are limited to plus or minus 25 percent so a real lighting change survives. It costs one extra decoding pass and no GPU. It fixes colour only: for likeness drift use drift_arrest on H3 Chain Settings.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| chain | SY_H3_CHAIN | yes | The chain to join: from a Render Segment (chain_state) or from Load Session. |  |
| crf | FLOAT | yes | Quality of the joined file. Lower is better and bigger. 0 is lossless. | 0.0 to 51.0, step 1.0, default 14.0 |
| stabilize | FLOAT | yes | 0 is off. 0.7 to 1.0 flattens the slow colour drift of the finished cut. Colour only. | 0.0 to 1.0, step 0.05, default 0.0 |

Outputs: `VIDEO`, `STRING`

## How to use

1. Connect chain: from the chain_state of an H3 Render Segment, or from H3 Load Session.
2. Set crf, the quality of the joined file. Lower is better and bigger, 0 is lossless.
3. Set stabilize (0 is off, 0.7 to 1.0 is the useful range) to flatten slow colour drift. It fixes colour only and adds one extra pass with no GPU use.
4. The joined video comes out, without the replayed opening of each segment, plus an info line.
