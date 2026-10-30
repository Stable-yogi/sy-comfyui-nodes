# Short ID SY (`SYShortID`)

Source: `nodes/sy_short_id.py`

**What it does:** Makes a short code such as a1b2c3d4. The same seed gives the same code. Add a prefix if you like.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| length | INT | yes | How many characters the code has (not counting the prefix). | 4 to 16, default 8 |
| charset | COMBO | yes | Which characters may appear: hex, letters, digits or mixed. | one of: hex, letters, digits, mixed |
| seed | INT | yes | Same seed gives the same code. Change it for a new code. | 0 to 18446744073709551615, default 0 |
| prefix | STRING | yes | Text put in front of the code, for example run_. | default '' |

Outputs: `STRING`
