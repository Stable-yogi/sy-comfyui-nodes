# Krea2TEnhancer SY (`SYKrea2TEnhancer`)

Source: `nodes/sy_krea2t_enhancer.py`

**What it does:** Makes Krea 2 Turbo follow the prompt more closely by boosting its text layers while the model runs.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The Krea 2 model to patch. A copy is returned; the original is not changed. |  |
| enabled | BOOLEAN | yes | Turn the effect on or off without removing the node. | default True |
| strength | FLOAT | yes | How strong the boost is. 0 does nothing, 1 is the normal setting, 2 is the maximum. | 0.0 to 2.0, step 0.05, default 1.0 |
| debug | BOOLEAN | yes | Print a few numbers to the console while sampling. | default False |

Outputs: `MODEL`

## How to use

1. Connect the Krea 2 model to model. A copy is patched; the original is not changed.
2. Set strength. 0 does nothing, 1 is normal and 2 is the maximum. enabled turns the effect off without removing the node.
3. The patched model comes out. It makes Krea 2 Turbo follow the prompt more closely. debug prints a few numbers to the console.
