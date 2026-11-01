# Prompt Choice SY (`SYPromptChoice`)

Source: `nodes/sy_prompt_wildcards.py`

**What it does:** Picks one option from each {red|green|blue} group in the text. The same seed gives the same result in the browser and in an API run. Use a backslash before a brace to keep it literal. The info line shows what each group picked and warns about a missing closing brace.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Your prompt. Write {red\|blue} to pick one option at random. | default '', multiline |
| seed | INT | yes | Same number gives the same picks every time. Change it to get other picks. | 0 to 18446744073709551615, default 0 |
| trim_options | BOOLEAN | no | On: spaces around an option are removed, so { red \| blue } gives red or blue. | default False |

Outputs: `STRING`, `STRING`
