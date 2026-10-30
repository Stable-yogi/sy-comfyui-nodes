# Krea2ConditioningRebalance SY (`SYKrea2ConditioningRebalance`)

Source: `nodes/sy_krea2_conditioning.py`

**What it does:** Rebalances Krea 2's 12 text layers one by one, then applies a global gain. Keeps the overall strength by default.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| conditioning | CONDITIONING | yes | The encoded prompt (positive or negative) to rebalance. |  |
| preset | COMBO | yes | Named per-layer gain profile. Pick custom to type your own gains below. | one of: balanced, detail, subtle, uniform, custom |
| per_layer_weights | STRING | yes | Comma-separated gains, one per text layer (12 for Krea 2). Used only when preset is custom. | default '1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.5, 5.0, 1.1, 4.0, 1.0' |
| multiplier | FLOAT | yes | Global gain after the per-layer gains. Keep near 1.0; higher values can oversaturate. | -1000.0 to 1000.0, step 0.01, default 1.0 |
| renormalize | BOOLEAN | yes | Keep the overall strength the same, so only the balance between layers changes. | default True |

Outputs: `CONDITIONING`
