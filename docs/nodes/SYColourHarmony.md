# Colour Harmony SY (`SYColourHarmony`)

Source: `nodes/sy_colour_harmony.py`

**What it does:** From one colour, makes a matching set of colours (opposite, three-way, four-way, neighbours) for a palette or overlay. Saturation and brightness stay the same.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| colour | STRING | yes | The starting colour as web hex, such as the default one. | default '#3366cc' |
| scheme | COMBO | yes | Which colours go with it: opposite, three-way, four-way, neighbours or split. | one of: complementary, triad, tetrad, analogous, split complementary |
| spread | FLOAT | yes | Degrees apart for analogous and split complementary. | 10.0 to 60.0, step 1.0, default 30.0 |

Outputs: `STRING`, `INT`

## How to use

1. Type the starting colour in **colour** as a web colour, for example #3366cc.
2. Pick **scheme**: complementary, triad, tetrad, analogous or split complementary.
3. Set **spread** for the degrees apart used by analogous and split complementary.
4. The outputs give the **palette** (the matching colours) and the **count** of colours.
