# Stacking Keeper SY (`SYStackingKeeper`)

Source: `nodes/sy_stacking_keeper.py`

**What it does:** Keeps the front-to-back stacking of your nodes. ComfyUI forgets it when a workflow is closed and opened again, so nodes you raised (Set and Get nodes for example) fall back behind others. Put one of these nodes anywhere in the workflow: it saves the stacking with the workflow and puts it back when you open it. It has no wires and never runs.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| order | STRING | yes | The saved stacking, back to front. Filled in by the node. | default '[]' |
| restore_on_open | BOOLEAN | yes | Put the saved stacking back when the workflow opens. | default True |

Outputs: none

## How to use

1. Add Stacking Keeper SY to the workflow. One is enough; put it anywhere (a corner is fine).
2. Work as usual. Every time you click a node to bring it to the front, or send it to the back, the node notes it.
3. Save the workflow. The stacking is saved with it. When you open the workflow, the nodes are put back in the saved order.
4. A node you added after the last save goes on top. A node you deleted is skipped.
5. The button **Put the stacking back now** raises every node again in the saved order. Turn **restore_on_open** off if you do not want it to happen by itself.

Subgraphs: put a Stacking Keeper SY inside the subgraph. Each graph keeps its own stacking, so each one that needs it gets its own keeper; the stacking comes back when you open the subgraph.

Tested on ComfyUI frontend 1.57.4, with real Set and Get nodes and with a subgraph. The first stacking of a freshly added keeper is taken from the nodes on screen; nodes off screen are put behind them.
