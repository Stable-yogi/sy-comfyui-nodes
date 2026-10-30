# Seed Stepper SY (`SYSeedStepper`)

Source: `nodes/sy_seed_stepper.py`

**What it does:** Builds a list of seeds (base, base+step, base+2*step...) and gives the seed at one index, plus the whole list.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| base_seed | INT | yes | The first seed of the list. | 0 to 18446744073709551615, default 0 |
| step | INT | yes | What is added to the seed for each next place. | -1000000 to 1000000, default 1 |
| count | INT | yes | How many seeds are in the list. | 1 to 256, default 4 |
| index | INT | yes | Which place of the list to give out. 0 is the first. | 0 to 100000, default 0 |
| wrap | BOOLEAN | yes | On: an index past the end starts over at the front. Off: that is an error. | default True |

Outputs: `INT`, `STRING`
