# Checkpoint Name Filter SY (`SYCheckpointNameFilter`)

Source: `nodes/sy_checkpoint_name_filter.py`

**What it does:** Looks through your checkpoint files and returns the name of the first one that contains your text.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| contains | STRING | yes | Part of the checkpoint name. Capital letters do not matter. | default '' |

Outputs: `STRING`, `INT`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'test_model.safetensors'; INT=int 1 |
| 2 | contains = '' (empty) | PASS | STRING=str 'test_model.safetensors'; INT=int 1 |

Note: this node refuses on purpose here (needs model files in the app's checkpoints folder, none are present here), so a plain-words refusal in any case is counted as REJECTED.


## Verdict

All 2 cases behaved as expected (2 passed, 0 rejected with a clear message).
