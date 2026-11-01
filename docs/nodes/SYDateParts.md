# Date Parts SY (`SYDateParts`)

Source: `nodes/sy_date_parts.py`

**What it does:** Splits a date into year, month, day, weekday name, day of the year and week number. Use today or type a date (2026-10-28, 20261028 and 2026/10/28 all work). Optional offset_days moves the date (-1 is yesterday). Also gives the date written in a format you pick, the month name, a weekend flag and an info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| mode | COMBO | yes | now uses today's date. from_text reads the date you type. | one of: now, from_text |
| date_text | STRING | yes | Date as YYYY-MM-DD. Only used in from_text mode. | default '2026-01-01' |
| offset_days | INT | no | Move the date by this many days. -1 is yesterday, 7 is next week. | -36500 to 36500, default 0 |
| date_format | COMBO | no | How the date_text output is written. | one of: YYYY-MM-DD, YYYYMMDD, YYYY/MM/DD, DD.MM.YYYY, DD-MM-YYYY, Month D, YYYY |

Outputs: `INT`, `INT`, `INT`, `STRING`, `INT`, `INT`, `STRING`, `STRING`, `BOOLEAN`, `STRING`

## How to use

1. Set mode: now uses today, from_text uses date_text (2026-10-28, 20261028 and 2026/10/28 all work).
2. Use offset_days to move the date (-1 is yesterday).
3. Pick date_format for the date_text output.
4. Outputs: year, month, day, weekday, day_of_year, week_number, date_text, month_name, is_weekend and info.
