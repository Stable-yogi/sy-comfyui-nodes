# Prompt Cleaner SY (`SYPromptCleaner`)

Source: `nodes/sy_prompt_cleaner.py`

**What it does:** Cleans a comma separated prompt: removes repeated tags, double commas and extra spaces. The order stays the same.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt to clean. Tags are split at commas. | default '', multiline |
| case_insensitive | BOOLEAN | yes | On: 'Cat' and 'cat' count as the same tag. The first one stays. | default True |

Outputs: `STRING`
