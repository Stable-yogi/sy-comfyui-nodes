# Text Number Format SY (`SYTextNumberFormat`)

Source: `nodes/sy_text_number_format.py`

**What it does:** Turns a number into text. Set decimals, zero padding (7 becomes 007), thousands commas, and a prefix and suffix.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| number | FLOAT | yes | The number to turn into text. | -1000000000000.0 to 1000000000000.0, step 0.01, default 0.0 |
| decimals | INT | yes | How many digits after the decimal point. | 0 to 10, default 0 |
| pad_width | INT | yes | Fill the whole-number part with leading zeros up to this width. | 0 to 32, default 0 |
| thousands | BOOLEAN | yes | Put commas between groups of three digits. | default False |
| prefix | STRING | yes | Text added before the number. | default '' |
| suffix | STRING | yes | Text added after the number. | default '' |
| number_in | * | no | Connect an INT or FLOAT here to use it instead of the number box. |  |

Outputs: `STRING`
