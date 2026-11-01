# Prompt Schedule SY (`SYPromptSchedule`)

Source: `nodes/sy_prompt_schedule.py`

**What it does:** Reads lines like '0: a cat' and '24: a dog' and gives the prompt that is active at the frame you choose. Also gives the next prompt and how far the frame is toward it (for blending), can repeat the schedule in a loop, and an info line says which key is in use.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | One line per key, written as frame: prompt. Blank lines and # lines are skipped. | default '0: a cat\n24: a dog', multiline |
| frame | INT | yes | The frame to look up. | 0 to 10000000, default 0 |
| loop_length | INT | no | 0 = no loop. Otherwise the schedule repeats every this many frames. | 0 to 10000000, default 0 |
| before_first | COMBO | no | What to give for frames before the first key: an empty prompt or the first prompt. | one of: empty, use first prompt |

Outputs: `STRING`, `INT`, `INT`, `STRING`, `FLOAT`, `STRING`

## How to use

1. Write one line per key in text, as frame: prompt. For example 0: a cat and 24: a dog. Blank lines and # lines are skipped.
2. Set frame to the frame to look up. The prompt output is the one active there.
3. Optional: loop_length repeats the schedule every that many frames (0 is off). before_first decides what frames before the first key get.
Other outputs: the next key frame, key count, next prompt, blend (how far toward the next prompt) and an info line.
