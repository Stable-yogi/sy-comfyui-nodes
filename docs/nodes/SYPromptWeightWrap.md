# Prompt Weight Wrap SY (`SYPromptWeightWrap`)

Source: `nodes/sy_prompt_weight_wrap.py`

**What it does:** Wraps a prompt as (text:1.2) with a weight, or in round, square or curly brackets. Empty text stays empty.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt part to wrap. | default '', multiline |
| style | COMBO | yes | How to wrap: with a weight number or with a bracket type. | one of: weight (text:1.2), round ( ), double round (( )), square [ ], curly { } |
| weight | FLOAT | yes | Strength for the weight style. 1 means no change. | 0.0 to 10.0, step 0.05, default 1.2 |

Outputs: `STRING`
