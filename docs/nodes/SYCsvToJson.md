# CSV To JSON SY (`SYCsvToJson`)

Source: `nodes/sy_csv_to_json.py`

**What it does:** Turns pasted table text (CSV or tab separated) into JSON. Pick the shape of the result. Numbers and true/false can become real JSON values.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| table | STRING | yes | The table as text, one row per line. Quoted cells may hold commas. | default '', multiline |
| has_header | BOOLEAN | yes | On: the first line holds column names. Off: columns are named col1, col2 and so on. | default True |
| delimiter | COMBO | yes | What separates the cells. Auto uses the one seen most in the first line. | one of: auto, comma, tab, semicolon, pipe |
| shape | COMBO | yes | How the JSON is laid out: one object per row, plain lists, or one list per column. | one of: list of objects, list of lists, object of columns |
| convert_numbers | BOOLEAN | yes | On: 30 becomes a number and true/false become booleans. Empty cells stay empty text. | default True |
| indent | INT | yes | Spaces of indentation in the JSON. 0 puts it all on one line. | 0 to 8, default 2 |
| on_error | COMBO | yes | Raise stops with a message. Empty text gives empty JSON text and 0 rows instead. | one of: raise, empty text |

Outputs: `STRING`, `INT`

## How to use

1. Paste or connect the table text to **table**.
2. Leave **delimiter** on auto, or pick the separator.
3. Turn **has_header** off if the first line is data.
4. Pick the **shape** you need and whether numbers should be converted.
5. Use **json_text** in the next node; **row_count** tells how many data rows were read.
