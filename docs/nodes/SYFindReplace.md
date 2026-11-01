# Find Replace SY (`SYFindReplace`)

Source: `nodes/sy_find_replace.py`

**What it does:** Finds text and replaces it: plain words, whole words only, or patterns (regex), with a limit on how many. A rules box applies a whole list of 'old => new' changes in one go. Gives the count and an info line that also says when a capital-letter difference was the reason nothing matched.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text you want to change. | default '', multiline |
| find | STRING | yes | The words to look for in the text. | default '' |
| replace | STRING | yes | What to put in place of every match. Empty removes the match. | default '' |
| use_regex | BOOLEAN | yes | On: Find is a pattern (regex) for advanced matching. Off: plain words. | default False |
| case_sensitive | BOOLEAN | yes | On: Cat and cat are different. Off: capital letters are ignored. | default True |
| whole_word | BOOLEAN | no | On: cat does not match inside category. Off: any match counts. | default False |
| max_count | INT | no | Replace only the first N matches. 0 means all of them. | 0 to 1000000, default 0 |
| rules | STRING | no | More changes, one per line: old => new. Run after the find above. Lines starting with # are skipped. | default '', multiline |

Outputs: `STRING`, `INT`, `STRING`
