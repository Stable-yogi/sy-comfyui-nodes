# Short ID SY (`SYShortID`)

Source: `nodes/sy_short_id.py`

**What it does:** Makes a short code such as a1b2c3d4. The same seed gives the same code, or switch on new code every run. Add a prefix if you like. The readable set avoids look-alike characters (0 o 1 l i). The info line says how many codes are possible.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| length | INT | yes | How many characters the code has (not counting the prefix). | 4 to 16, default 8 |
| charset | COMBO | yes | Which characters may appear: hex, letters, digits, mixed, or readable (no look-alikes). | one of: hex, letters, digits, mixed, readable |
| seed | INT | yes | Same seed gives the same code. Change it for a new code. | 0 to 18446744073709551615, default 0 |
| prefix | STRING | yes | Text put in front of the code, for example run_. | default '' |
| new_each_run | BOOLEAN | no | On: a different code on every run, whatever the seed. Off: the seed decides. | default False |

Outputs: `STRING`, `STRING`
