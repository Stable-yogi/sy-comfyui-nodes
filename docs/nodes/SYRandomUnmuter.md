# RandomUnmuter SY (`SYRandomUnmuter`)

Source: `nodes/sy_random_unmuter.py`

**What it does:** Before each run it switches ON one node out of a set and switches the rest OFF, so every run uses a different one. The set is every node whose title holds one of your words. Pick at random or one after the other. It has no wires.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| title_filter | STRING | yes | Words separated by commas. Every node whose title holds one of them is in the set. Rename nodes to group them. | default '' |
| pick | COMBO | yes | random picks any one. round_robin goes through the set one by one. | one of: random, round_robin |
| seed | INT | yes | 0 picks differently every time. Any other number gives the same order again and again. | 0 to 2147483647, default 0 |
| off_mode | COMBO | yes | What happens to the nodes that are not picked. Mute stops them. Bypass lets the picture pass through. | one of: Mute, Bypass |
| enabled | BOOLEAN | yes | Off leaves your nodes exactly as they are. | default True |

Outputs: none

## How to use

1. Give the candidate nodes a common word in their title (for example "look A", "look B", "look C").
2. Add Random Unmuter SY and write that word in title_filter (several words are separated by commas).
3. Pick random or round_robin. With seed 0 the pick is different each time. Any other seed repeats the same order.
4. off_mode decides what happens to the nodes that are not picked: Mute stops them, Bypass lets the picture pass through.
Before every run exactly one node of the set is switched on and the others off. Turn enabled off to leave your nodes as they are. A filter that is empty touches nothing. It has no wires.
