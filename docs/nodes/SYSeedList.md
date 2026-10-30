# Seed List SY (`SYSeedList`)

Source: `nodes/sy_seed_list.py`

**What it does:** Makes a comma list of seeds. Sequential counts up. Random fixed looks random but is the same every run.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| base_seed | INT | yes | Start number. Same start gives the same list. | 0 to 18446744073709551615, default 0 |
| count | INT | yes | How many seeds to make (1 to 64). | 1 to 64, default 4 |
| mode | COMBO | yes | Sequential: base, base+1... Random fixed: scattered numbers, repeatable. | one of: sequential, random_fixed |

Outputs: `STRING`, `INT`
