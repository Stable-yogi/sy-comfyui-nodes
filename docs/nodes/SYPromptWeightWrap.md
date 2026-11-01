# Prompt Weight Wrap SY (`SYPromptWeightWrap`)

Source: `nodes/sy_prompt_weight_wrap.py`

**What it does:** Wraps a prompt as (text:1.2) with a weight, or in round, square or curly brackets. Can wrap every tag on its own, avoids double wrapping like ((cat:1.2):1.2), and warns about unmatched brackets.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt part to wrap. | default '', multiline |
| style | COMBO | yes | How to wrap: with a weight number or with a bracket type. | one of: weight (text:1.2), round ( ), double round (( )), square [ ], curly { } |
| weight | FLOAT | yes | Strength for the weight style. 1 means no change. | 0.0 to 10.0, step 0.05, default 1.2 |
| each_tag | BOOLEAN | no | On: wrap every comma tag on its own, like (cat:1.2), (dog:1.2). | default False |
| already_weighted | COMBO | no | What to do with a tag already written like (cat:1.3): wrap again, change its weight, or skip it. | one of: wrap again, replace the weight, leave as it is |

Outputs: `STRING`, `STRING`

## How to use

1. Put the prompt part in text.
2. Choose style: a weight like (text:1.2), or round, square or curly brackets. Set weight for the weight style.
3. Turn each_tag on to wrap every comma tag on its own.
4. already_weighted decides what happens to a tag like (cat:1.3): wrap again, replace the weight, or leave it.
The info output warns about unmatched brackets.
