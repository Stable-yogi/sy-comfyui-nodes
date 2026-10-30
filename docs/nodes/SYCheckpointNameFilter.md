# Checkpoint Name Filter SY (`SYCheckpointNameFilter`)

Source: `nodes/sy_checkpoint_name_filter.py`

**What it does:** Looks through your checkpoint files and returns the name of the first one that contains your text.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| contains | STRING | yes | Part of the checkpoint name. Capital letters do not matter. | default '' |

Outputs: `STRING`, `INT`
