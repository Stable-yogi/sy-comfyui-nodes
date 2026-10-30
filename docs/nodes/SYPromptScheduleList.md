# Prompt Schedule List SY (`SYPromptScheduleList`)

Source: `nodes/sy_prompt_schedule_list.py`

**What it does:** Turns a prompt schedule into a list with one prompt per frame, one per line. Also tells how many segments it has.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | One line per key, written as frame: prompt. Blank lines and # lines are skipped. | default '0: a cat\n24: a dog', multiline |
| total_frames | INT | yes | How many frames to list. The most allowed is 2000. | 1 to 2000, default 48 |

Outputs: `STRING`, `INT`
