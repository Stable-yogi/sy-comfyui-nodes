# Progress Bar SY (`SYProgressBar`)

Source: `nodes/sy_progress_bar.py`

**What it does:** Shows a bar at the top (or bottom) of the screen while a workflow runs: percent done, the step of the running node, which node is running and the time. Good for screen recordings. Put one in the workflow; it has no wires.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| enabled | BOOLEAN | yes | Off hides the bar. | default True |
| position | COMBO | yes | Show the bar at the top or the bottom of the screen. | one of: top, bottom |
| show_node | BOOLEAN | yes | Show the title of the node that is running now. | default True |
| show_time | BOOLEAN | yes | Show the time since the run started. | default True |
| show_step | BOOLEAN | yes | Show the step counter of the running node, for example step 12 of 30. | default True |

Outputs: none

## How to use

1. Put one Progress Bar SY anywhere in the workflow. It has no wires.
2. Press Queue. A bar shows at the top (or bottom) of the screen with percent, step, the running node and the time.
3. Turn **show_node**, **show_time** or **show_step** off for a cleaner bar. Turn **enabled** off to hide it.
4. The bar is an estimate from the number of nodes that run, so it can jump when cached nodes are skipped.
