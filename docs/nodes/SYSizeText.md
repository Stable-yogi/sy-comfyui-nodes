# Size Text SY (`SYSizeText`)

Source: `nodes/sy_size_text.py`

**What it does:** Turns a number of bytes into easy text such as 1.5 GB. Useful for file size labels. Pick a fixed unit (like GB) to compare sizes, and use the number output for maths. The info line shows the bytes and the base used.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| bytes | INT | yes | The size in bytes. | 0 to 9007199254740991, default 1048576 |
| base | COMBO | yes | 1024 is what most computers use; 1000 is what disk makers use. | one of: 1024, 1000 |
| decimals | INT | yes | How many digits to show after the decimal point. | 0 to 4, default 1 |
| unit | COMBO | no | auto picks the best unit. Choose GB to always get gigabytes, like 0.5 GB. | one of: auto, B, KB, MB, GB, TB |

Outputs: `STRING`, `FLOAT`, `STRING`

## How to use

1. Type or connect a size in bytes.
2. Pick base (1024 or 1000), decimals, and a unit. auto picks the best one, or choose a fixed unit such as GB to compare sizes.
3. The text (for example 1.5 GB) and a number come out. Use the number for maths.
