# Bool Logic SY (`SYBoolLogic`)

Source: `nodes/sy_bool_logic.py`

**What it does:** Combines two yes/no values with and, or, xor, nand, nor or xnor. The not choice flips a and ignores b. The info line shows what went in.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| a | BOOLEAN | yes | The first yes/no value. | default False |
| b | BOOLEAN | yes | The second yes/no value. Not used by not. | default False |
| operation | COMBO | yes | and: both yes. or: one or more. xor: exactly one. not: flip a. nand/nor/xnor: the opposite of and/or/xor. | one of: and, or, xor, not, nand, nor, xnor |

Outputs: `BOOLEAN`, `STRING`

## How to use

1. Connect or set two yes/no values in a and b.
2. Pick operation: and, or, xor, nand, nor, xnor. The choice not flips a and ignores b.
3. The answer comes out as result, with an info line that shows what went in.
