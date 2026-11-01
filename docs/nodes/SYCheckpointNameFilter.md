# Checkpoint Name Filter SY (`SYCheckpointNameFilter`)

Source: `nodes/sy_checkpoint_name_filter.py`

**What it does:** Looks through your checkpoint files and returns the name of the one that contains your words. Adds over a plain search: several words at once ('flux dev'), words to leave out, an index that wraps to step through the matches, the full list of matches and a plain info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| contains | STRING | yes | Part of the checkpoint name, for example 'flux dev'. Capitals do not matter. | default '' |
| exclude | STRING | no | Words that must NOT be in the name, for example 'fp8 old'. | default '' |
| index | INT | no | Which match to use, from 0. A too big number wraps to the start. | 0 to 2147483647, default 0 |

Outputs: `STRING`, `INT`, `STRING`, `STRING`

## How to use

1. Type words in contains, for example flux dev. Several words work at once.
2. Add words to leave out in exclude.
3. Use index to step through the matches. It wraps around.
4. Outputs: name, match_count, all_matches and info.
