# Prompt Schedule List SY (`SYPromptScheduleList`)

Source: `nodes/sy_prompt_schedule_list.py`

**What it does:** Turns a prompt schedule into one prompt per frame, one per line. Adds over a plain loop: it can fill the frames before the first key, and the info line warns about a missing 0 key or keys past the last frame.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | One line per key, written as frame: prompt. Blank lines and # lines are skipped. | default '0: a cat\n24: a dog', multiline |
| total_frames | INT | yes | How many frames to list. The most allowed is 2000. | 1 to 2000, default 48 |
| fill_before_first | BOOLEAN | no | On: frames before the first key use the first prompt instead of an empty line. | default False |

Outputs: `STRING`, `INT`, `STRING`

## How to use

1. Write one line per key in text, as frame: prompt. Blank lines and # lines are skipped.
2. Set total_frames (the most allowed is 2000).
3. Turn fill_before_first on so frames before the first key use the first prompt instead of an empty line.
Outputs: one prompt per frame, one per line, the number of segments and an info line. The info line warns about a missing 0 key or keys past the last frame.
