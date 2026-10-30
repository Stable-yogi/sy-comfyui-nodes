# Sort Dedupe Lines SY (`SYSortDedupeLines`)

Source: `nodes/sy_sort_dedupe_lines.py`

**What it does:** Cleans a list with one item per line: sorts it, removes repeated lines and drops empty ones.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The list, one item per line. | default '', multiline |
| sort | COMBO | yes | How to order the lines. none keeps the original order. | one of: none, a-z, z-a, shortest first, longest first |
| remove_duplicates | BOOLEAN | yes | On keeps only the first copy of each line. | default True |
| ignore_case | BOOLEAN | yes | On treats capital and small letters as the same when comparing and sorting. | default True |
| drop_empty | BOOLEAN | yes | On removes lines that are empty or only spaces. | default True |

Outputs: `STRING`, `INT`
