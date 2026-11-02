# Table Pick SY (`SYTablePick`)

Source: `nodes/sy_table_pick.py`

**What it does:** Takes one cell from pasted table text (CSV or tab separated). Choose the row and a column name or number. If the cell does not exist you get your default text and found is off.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| table | STRING | yes | The table as text, one row per line. Quoted cells may hold commas. | default '', multiline |
| row | INT | yes | Which data row to read. 0 is the first row after the header. | 0 to 100000, default 0 |
| column | STRING | yes | A column name from the header, or a number starting at 1. | default '1' |
| has_header | BOOLEAN | yes | On: the first line holds column names and is not a data row. | default True |
| delimiter | COMBO | yes | What separates the cells. Auto uses the one seen most in the first line. | one of: auto, comma, tab, semicolon, pipe |
| default | STRING | yes | Text to give back when the row or cell does not exist. | default '' |

Outputs: `STRING`, `BOOLEAN`, `INT`

## How to use

1. Paste the table text into **table**.
2. Leave **delimiter** on auto, or pick the separator.
3. Type the column name (or its number from 1) into **column**.
4. Set **row**: 0 is the first data row.
5. Use **value** for the cell. Check **found** to know if it really existed. A column name that is not in the header stops the run with a message.
