# Global Seed SY (`SYGlobalSeed`)

Source: `nodes/sy_global_seed.py`

**What it does:** One seed for the whole graph. Before each run it writes this seed into every other node that has a seed box (seed, noise_seed), with no wires. Then it picks the next seed by the mode. The seed also comes out of the node.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| seed | INT | yes | The seed for the next run. It goes into every other seed box in the graph. | 0 to 9007199254740991, default 0 |
| mode | COMBO | yes | What happens after each run: fixed keeps the seed, random picks a new one, increment adds 1, decrement takes 1. | one of: fixed, random, increment, decrement |
| apply_to_all | BOOLEAN | yes | On writes the seed into the other seed boxes. Off leaves them alone (only the output is used). | default True |
| skip_titles | STRING | no | Nodes whose title holds one of these words (comma separated) keep their own seed. | default '' |

Outputs: `INT`

## How to use

1. Put one Global Seed SY anywhere in the workflow. It has no wires.
2. Type the **seed** you want. Before each run it is written into every other node that has a seed or noise_seed box.
3. Pick **mode**: fixed keeps it, random picks a new seed after each run, increment adds 1, decrement takes 1.
4. Add words to **skip_titles** (comma separated) for nodes that must keep their own seed. Turn **apply_to_all** off to use only the output.
