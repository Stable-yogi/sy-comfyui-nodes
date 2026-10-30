# Size Text SY (`SYSizeText`)

Source: `nodes/sy_size_text.py`

**What it does:** Turns a number of bytes into easy text such as 1.5 GB. Useful for file size labels.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| bytes | INT | yes | The size in bytes. | 0 to 9007199254740991, default 1048576 |
| base | COMBO | yes | 1024 is what most computers use; 1000 is what disk makers use. | one of: 1024, 1000 |
| decimals | INT | yes | How many digits to show after the decimal point. | 0 to 4, default 1 |

Outputs: `STRING`
