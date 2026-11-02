# Prompt Conflict Check SY (`SYPromptConflictCheck`)

Source: `nodes/sy_prompt_conflict_check.py`

**What it does:** Warns when a prompt holds opposite words like day and night or indoor and outdoor. The text passes through unchanged. You can add your own pairs.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt to check. | default '', multiline |
| extra_pairs | STRING | no | Your own opposite pairs, one per line, like: cat \| dog | default '', multiline |

Outputs: `STRING`, `STRING`, `INT`

## How to use

1. Connect your prompt to **text**. It passes through unchanged on the **text** output.
2. Optionally type your own opposite pairs in **extra_pairs**, one per line, for example: cat | dog.
3. Read the **report** output for any pairs found, for example day and night in the same prompt.
4. The **count** output is the number of conflicts found. 0 means none.
