# CyclePick SY (`SYCyclePick`)

Source: `nodes/sy_cycle_pick.py`

**What it does:** Picks one line from a list using a counter. When the counter passes the end it starts again from the first line, or bounces back (ping-pong), or stays on the last. Can skip # comment lines.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| items | STRING | yes | One item per line. Blank lines are skipped. | default '', multiline |
| counter | INT | yes | Which item to take, counting from 0. It goes round when too big. | -2147483648 to 2147483647, default 0 |
| mode | COMBO | no | loop: 0 1 2 0 1 2. ping-pong: 0 1 2 1 0 1. stop at last: 0 1 2 2 2. | one of: loop, ping-pong, stop at last |
| skip_comments | BOOLEAN | no | On skips lines that start with #, so you can switch items off. | default False |

Outputs: `STRING`, `INT`, `INT`, `STRING`

## How to use

1. Write the list in items, one line each.
2. Feed a number to counter.
3. Pick mode: loop starts again at the first line, ping-pong bounces back, stop at last stays on the last.
4. Turn on skip_comments to ignore lines that start with #. Outputs: item, index, count and info.
