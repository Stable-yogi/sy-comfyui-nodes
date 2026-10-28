# Krea2TEnhancerAdvanced SY (`SYKrea2TEnhancerAdvanced`)

Source: `nodes/sy_krea2t_enhancer.py`

**What it does:** Like Krea2T Enhancer, plus a text scale that makes the whole prompt louder or quieter.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The Krea 2 model to patch. A copy is returned; the original is not changed. |  |
| enabled | BOOLEAN | yes | Turn the effect on or off without removing the node. | default True |
| strength | FLOAT | yes | How strong the boost is. 0 does nothing, 1 is the normal setting, 2 is the maximum. | 0.0 to 2.0, step 0.05, default 1.0 |
| text_scale | FLOAT | yes | Makes the prompt text louder (above 1) or quieter (below 1) after the text MLP. | 0.25 to 4.0, step 0.05, default 1.0 |
| debug | BOOLEAN | yes | Print a few numbers to the console while sampling. | default False |

Outputs: `MODEL`

## How it was tested

This node was not run by the harness. Reason: Torch run with a tiny fake model passed. Not run on a real Krea 2 model yet. Source quirk kept: a wrong text-fusion shape raises an error.


## Verdict

Not run. Torch run with a tiny fake model passed. Not run on a real Krea 2 model yet. Source quirk kept: a wrong text-fusion shape raises an error.
