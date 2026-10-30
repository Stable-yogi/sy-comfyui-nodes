# Find Replace SY (`SYFindReplace`)

Source: `nodes/sy_find_replace.py`

**What it does:** Finds text and replaces it. Turn on use_regex for patterns. Also gives the number of replacements.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text you want to change. | default '', multiline |
| find | STRING | yes | The words to look for in the text. | default '' |
| replace | STRING | yes | What to put in place of every match. Empty removes the match. | default '' |
| use_regex | BOOLEAN | yes | On: Find is a pattern (regex) for advanced matching. Off: plain words. | default False |
| case_sensitive | BOOLEAN | yes | On: Cat and cat are different. Off: capital letters are ignored. | default True |

Outputs: `STRING`, `INT`
