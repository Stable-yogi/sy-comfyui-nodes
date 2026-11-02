# Text Extract Numbers SY (`SYTextExtractNumbers`)

Source: `nodes/sy_text_extract_numbers.py`

**What it does:** Pulls the numbers out of a text. Handles 1,234.5 and -7. Reads 1e3 as 1 and 3, and finds numbers inside words like abc123. No numbers found gives empty text and count 0.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to search for numbers. | default '', multiline |
| kind | COMBO | yes | Which numbers to keep: all, only whole numbers, or only numbers with a decimal point. | one of: all numbers, whole numbers only, decimals only |
| allow_negative | BOOLEAN | yes | On: a minus sign in front of a number makes it negative. Off: the minus is ignored. | default True |
| thousands | COMBO | yes | Whether 1,234 is one number or two (1 and 234). | one of: ignore, commas are thousands separators |
| pick | COMBO | yes | Keep all numbers, or only the first, last, largest or smallest one. | one of: all, first, last, largest, smallest |
| separator | STRING | yes | Text put between the numbers in the output. | default ', ' |

Outputs: `STRING`, `INT`, `FLOAT`, `FLOAT`

## How to use

1. Connect the text to **text**.
2. Choose **kind** and whether commas are thousands separators.
3. Use **pick** to keep only the first, last, largest or smallest number.
4. Read **numbers**, **count**, **total** and **first**.
