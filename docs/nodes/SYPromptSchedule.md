# Prompt Schedule SY (`SYPromptSchedule`)

Source: `nodes/sy_prompt_schedule.py`

**What it does:** Reads lines like '0: a cat' and '24: a dog' and gives the prompt that is active at the frame you choose.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | One line per key, written as frame: prompt. Blank lines and # lines are skipped. | default '0: a cat\n24: a dog', multiline |
| frame | INT | yes | The frame to look up. | 0 to 10000000, default 0 |

Outputs: `STRING`, `INT`, `INT`
