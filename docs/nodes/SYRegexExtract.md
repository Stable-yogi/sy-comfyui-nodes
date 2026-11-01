# Regex Extract SY (`SYRegexExtract`)

Source: `nodes/sy_regex_extract.py`

**What it does:** Finds the first match of a regular expression in a text and gives one group of it, or a default. Can join all matches, and the info line says where it matched or why not. Limits: pattern 200, text 100000 characters.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to search in (up to 100000 characters). | default '', multiline |
| pattern | STRING | yes | Regular expression to look for (up to 200 characters). | default '(\\d+)' |
| group | INT | yes | Which bracket group to return. 0 is the whole match. | 0 to 99, default 1 |
| default | STRING | yes | Text to return when nothing matches. | default '' |
| ignore_case | BOOLEAN | yes | Treat upper and lower case letters as the same. | default False |
| find_all | BOOLEAN | no | On: collect every match, not just the first, and join them. | default False |
| join_with | STRING | no | Put between matches when find_all is on, for example a comma or a new line. | default ', ' |

Outputs: `STRING`, `BOOLEAN`, `STRING`
