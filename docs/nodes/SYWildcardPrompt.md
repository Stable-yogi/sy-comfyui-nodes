# Wildcard Prompt SY (`SYWildcardPrompt`)

Source: `nodes/sy_wildcard_prompt.py`

**What it does:** One prompt with random variety. Write {red|blue|green} to pick one, {2$$a|b|c} to pick two different, __name__ to take a line from a wildcard list. Same seed gives the same prompt. Step through walks every combination with one number. Shows what was picked. Lists come from the wildcards box or from wildcards/<name>.txt in the input folder. Replaces a prompt-random node plus a list loader plus a text note.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Template. {a\|b} picks one, {2$$a\|b\|c} two, __name__ a list line. Example: a {red\|blue} coat | default 'a {red\|blue\|green} coat at {sunrise\|sunset}', multiline |
| seed | INT | yes | Same seed gives the same prompt. Example: 12345 | 0 to 18446744073709551615, default 0 |
| mode | COMBO | yes | random from seed, or step through the combinations with index. | one of: random from seed, step through (index) |
| wildcards | STRING | no | Lists, one per line: name: first \| second \| third. Example: hair: red \| blonde | default '', multiline |
| index | INT | no | Step-through number: 0, 1, 2 ... walks every combination, then repeats. | 0 to 9007199254740991, default 0 |
| enabled | BOOLEAN | no | Off passes the text through unchanged, braces and all. | default True |

Outputs: `STRING`, `STRING`, `STRING`
