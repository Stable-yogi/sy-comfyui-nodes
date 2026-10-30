# Timestamp SY (`SYTimestamp`)

Source: `nodes/sy_timestamp.py`

**What it does:** Gives the current date and time as text. Handy for file names, folders and notes.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| format | COMBO | yes | Which look the text has. Compact has no separators. Unix is seconds. | one of: date, time, date_time, compact, unix |
| use_utc | BOOLEAN | yes | On: use world time (UTC). Off: use the clock of this computer. | default False |

Outputs: `STRING`
