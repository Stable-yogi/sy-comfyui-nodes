# Prompt Diff SY (`SYPromptDiff`)

Source: `nodes/sy_prompt_diff.py`

**What it does:** Compares the tags of two prompts. Gives the tags only in A, only in B and shared by both, with counts, a similarity number from 0 to 1 and a plain summary. Can ignore weights, so (cat:1.2) matches cat.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text_a | STRING | yes | The first prompt. | default '', multiline |
| text_b | STRING | yes | The second prompt to compare with the first. | default '', multiline |
| separator | STRING | yes | The character that splits one tag from the next. | default ',' |
| ignore_weights | BOOLEAN | no | On: (cat:1.2), [cat] and cat count as the same tag. | default False |

Outputs: `STRING`, `STRING`, `STRING`, `INT`, `INT`, `INT`, `FLOAT`, `STRING`
