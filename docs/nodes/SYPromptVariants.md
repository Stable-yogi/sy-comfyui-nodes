# Prompt Variants SY (`SYPromptVariants`)

Source: `nodes/sy_prompt_variants.py`

**What it does:** Turns a template with {red|blue|green} choices into every combination. Returns one picked by index (wraps around) plus the full list for batch runs.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| template | STRING | yes | Text with choices in braces, like {red\|blue}. Use \{ for a plain brace. | default 'a {red\|blue\|green} car', multiline |
| index | INT | yes | Which combination to return. Too big a number wraps around. | 0 to 100000, default 0 |
| max_combinations | INT | yes | Most combinations to list in all_text. | 1 to 10000, default 500 |

Outputs: `STRING`, `STRING`, `INT`

## How to use

1. Write a **template** with choices in braces separated by bars, for example a {red|blue|green} car.
2. Set **index** to pick one combination. 0 gives the first, 1 the second. A number that is too big wraps around.
3. Use the **text** output as the picked prompt.
4. For batch runs use **all_text**, which lists every combination up to **max_combinations** (for example 500). **count** says how many there are.
