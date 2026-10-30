# DateParts SY (`SYDateParts`)

Source: `nodes/sy_date_parts.py`

**What it does:** Splits a date into year, month, day, weekday name, day of the year and week number. Use today or type a date.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | now uses today's date. from_text reads the date you type. | one of: now, from_text |
| date_text | STRING | yes | Date as YYYY-MM-DD. Only used in from_text mode. | default '2026-01-01' |

Outputs: `INT`, `INT`, `INT`, `STRING`, `INT`, `INT`
