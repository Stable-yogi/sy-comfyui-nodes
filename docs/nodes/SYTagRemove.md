# Tag Remove SY (`SYTagRemove`)

Source: `nodes/sy_tag_remove.py`

**What it does:** Takes unwanted tags or words out of a comma separated prompt. Keeps the order of the rest and tells you what it removed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt, tags separated by commas. | default '', multiline |
| remove | STRING | yes | Tags to take out. One per line or separated by commas. | default '', multiline |
| match | COMBO | yes | Exact tag: whole tag must match. Contains word: the word may sit inside a longer tag. | one of: exact tag, tag contains word |
| ignore_case | BOOLEAN | yes | On: Red and red count as the same. | default True |

Outputs: `STRING`, `STRING`, `INT`

## How to use

1. Connect a comma separated prompt to **text**.
2. Type the tags to take out in **remove**, one per line or separated by commas, for example blurry, watermark.
3. Pick **match**: exact tag needs the whole tag to match, tag contains word also removes longer tags holding the word.
4. Leave **ignore_case** on so Red and red count as the same.
5. The **text** output is the cleaned prompt, **removed** lists what was taken out, and **count** says how many.
