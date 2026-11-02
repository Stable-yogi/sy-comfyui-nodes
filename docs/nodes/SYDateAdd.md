# Date Add SY (`SYDateAdd`)

Source: `nodes/sy_date_add.py`

**What it does:** Adds days, weeks, months, years or business days to a date. Months and years stay on the last day of a short month. Business days skip weekends but not holidays.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| date | STRING | yes | The start date: YYYY-MM-DD, DD/MM/YYYY, or the word today. | default '2026-01-31' |
| amount | INT | yes | How many units to add. A negative number goes back in time. | -100000 to 100000, default 7 |
| unit | COMBO | yes | What the amount counts. Business days skip Saturday and Sunday. | one of: days, weeks, months, years, business days |
| output_format | COMBO | yes | How the result date is written. | one of: YYYY-MM-DD, DD/MM/YYYY, D Month YYYY, weekday, D Month YYYY |

Outputs: `STRING`, `STRING`, `INT`, `INT`

## How to use

1. Type the start date in **date**, or write today.
2. Set **amount** and **unit**.
3. Pick the **output_format**.
4. Use **date**, **weekday**, **day_of_year** and **days_between** as needed.
