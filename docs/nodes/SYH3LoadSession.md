# H3 Load Session SY (`SYH3LoadSession`)

Source: `nodes/sy_h3_chain.py`

**What it does:** Pick up a session that is already on disk, to re-join it, feed the repair node or extend it, without re-rendering anything.

Its chain output wires into H3 Chain To Video and H3 Repair Segment, and also into another H3 Render Segment's chain_state, to render more shots onto the end of a finished session.

handoff_mode is which form of the last segment's ending to load. Match the chain that will use it. It falls back to 'pixel' if the session has no latent ending.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| session_name | STRING | yes | Folder name of the session to load, under output/h3_continuous/. | default 'my_chain' |
| handoff_mode | COMBO | yes | Which form of the last ending to load. 'latent' falls back to 'pixel' if the session has none. | one of: latent, pixel |

Outputs: `SY_H3_CHAIN`, `STRING`
