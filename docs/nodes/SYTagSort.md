# Tag Sort SY (`SYTagSort`)

Source: `nodes/sy_tag_sort.py`

**What it does:** Splits a prompt into tags, then sorts them (A to Z, by length, or a repeatable shuffle) and removes repeats.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt whose tags you want to sort. | default '', multiline |
| separator | STRING | yes | The character that splits one tag from the next. | default ',' |
| order | COMBO | yes | keep = same order. Others sort A to Z, by length, or shuffle the same way every time. | one of: keep, alphabetical, shortest_first, longest_first, shuffle_seeded |
| seed | INT | yes | Number for the shuffle. The same number gives the same order. | 0 to 9223372036854775807, default 0 |
| dedupe | BOOLEAN | yes | On: remove tags that appear twice (capital letters are ignored). | default True |

Outputs: `STRING`
