# Prompt Cleaner SY (`SYPromptCleaner`)

Source: `nodes/sy_prompt_cleaner.py`

**What it does:** Cleans a comma separated prompt: removes repeated tags, double commas and extra spaces. The order stays the same. Can treat (cat:1.2) as cat, drop tags you list, and lowercase everything. An info line says what was removed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt to clean. Tags are split at commas. | default '', multiline |
| case_insensitive | BOOLEAN | yes | On: 'Cat' and 'cat' count as the same tag. The first one stays. | default True |
| ignore_weights | BOOLEAN | no | On: (cat:1.2), [cat] and cat count as the same tag. The first one stays. | default False |
| drop_tags | STRING | no | Tags to remove, separated by commas. Matched the same way as repeats. | default '' |
| lowercase | BOOLEAN | no | On: write every tag in lowercase. | default False |

Outputs: `STRING`, `INT`, `STRING`

## How to use

1. Paste your comma separated prompt into text.
2. The node removes repeated tags, double commas and extra spaces. The order stays the same.
3. Optional: ignore_weights treats (cat:1.2) as cat, drop_tags removes tags you list, lowercase writes everything in lowercase. case_insensitive counts Cat and cat as the same tag.
Outputs: the clean text, how many tags were removed and an info line.
