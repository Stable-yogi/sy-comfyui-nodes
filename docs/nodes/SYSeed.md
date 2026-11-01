# Seed SY (`SYSeed`)

Source: `nodes/sy_seed.py`

**What it does:** Gives one seed number. Fixed keeps it. Random picks a new one each run. Increment adds 1 each run. Also gives the seed as text (for file names) and an info line, and can limit the seed to 53-bit or 32-bit so it is never too big for the browser or an older node.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seed | INT | yes | The seed number. Same number gives the same picture. | 0 to 18446744073709551615, default 0 |
| mode | COMBO | yes | Fixed keeps the number. Random picks a new one each run. Increment adds 1 each run. | one of: fixed, random, increment |
| seed_range | COMBO | no | Biggest seed allowed. Pick 53-bit if a seed loses digits in the browser, 32-bit for older nodes. | one of: 64-bit, 53-bit (browser safe), 32-bit |

Outputs: `INT`, `STRING`, `STRING`

## How to use

1. Type a seed and pick mode: fixed keeps it, random picks a new one each run, increment adds 1 each run.
2. Set seed_range to 53-bit if a seed loses digits in the browser, or 32-bit for older nodes.
3. Connect the seed output to a sampler. The text output is the same seed as text, for file names.
