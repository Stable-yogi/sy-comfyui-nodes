# Case Style Convert SY (`SYCaseStyleConvert`)

Source: `nodes/sy_case_style_convert.py`

**What it does:** Rewrites a phrase into another naming style, for file names, keys or tags. Spaces, dashes, underscores and capital letters mark where the words split.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The phrase to rewrite. Other symbols are dropped. | default '' |
| style | COMBO | yes | The naming style you want the phrase in. | one of: snake_case, kebab-case, camelCase, PascalCase, Title Case, UPPER_SNAKE |

Outputs: `STRING`

## How to use

1. Type or connect the phrase to **text**.
2. Pick the wanted naming style in **style**, for example snake_case or Title Case.
3. The output **text** is the phrase in that style, ready to use as a file name, key or tag.
