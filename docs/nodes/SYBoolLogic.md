# Bool Logic SY (`SYBoolLogic`)

Source: `nodes/sy_bool_logic.py`

**What it does:** Combines two yes/no values with and, or, xor. The not choice flips a and ignores b.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| a | BOOLEAN | yes | The first yes/no value. | default False |
| b | BOOLEAN | yes | The second yes/no value. Not used by not. | default False |
| operation | COMBO | yes | and: both yes. or: at least one yes. xor: exactly one yes. not: flip a. | one of: and, or, xor, not |

Outputs: `BOOLEAN`
