# Prompt Diff SY (`SYPromptDiff`)

Source: `nodes/sy_prompt_diff.py`

**What it does:** Compares the tags of two prompts. Gives the tags only in A, only in B and shared by both, with counts.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text_a | STRING | yes | The first prompt. | default '', multiline |
| text_b | STRING | yes | The second prompt to compare with the first. | default '', multiline |
| separator | STRING | yes | The character that splits one tag from the next. | default ',' |

Outputs: `STRING`, `STRING`, `STRING`, `INT`, `INT`, `INT`
