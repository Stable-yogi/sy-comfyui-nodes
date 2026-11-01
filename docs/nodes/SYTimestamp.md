# Timestamp SY (`SYTimestamp`)

Source: `nodes/sy_timestamp.py`

**What it does:** Gives the current date and time as text. Handy for file names, folders and notes. Type your own pattern (for example %Y%m%d_%H%M) to get exactly the look you want. Also gives the unix seconds as a number and an info line saying which clock was used.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| format | COMBO | yes | Which look the text has. Compact has no separators. Unix is seconds. | one of: date, time, date_time, compact, unix |
| use_utc | BOOLEAN | yes | On: use world time (UTC). Off: use the clock of this computer. | default False |
| custom_format | STRING | no | Your own pattern, for example %Y%m%d_%H%M. Empty uses the format above. | default '' |
| filename_safe | BOOLEAN | no | For the custom pattern: turn characters that cannot be in a file name (: / and so on) into dashes. | default True |

Outputs: `STRING`, `INT`, `STRING`

## How to use

1. Pick format: date, time, date_time, compact or unix (seconds).
2. Turn on use_utc for world time, or leave it off for this computer's clock.
3. Optional: type a custom_format such as %Y%m%d_%H%M. filename_safe turns characters that cannot be in a file name into dashes.
4. Outputs: the text, the unix seconds and an info line.
