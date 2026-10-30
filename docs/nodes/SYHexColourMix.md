# HexColourMix SY (`SYHexColourMix`)

Source: `nodes/sy_hex_colour_mix.py`

**What it does:** Blends two colours given as hex text. Amount 0 keeps the first colour and 1 gives the second.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| colour_a | STRING | yes | First colour as 3 or 6 hex digits. The # sign is optional. | default '000000' |
| colour_b | STRING | yes | Second colour as 3 or 6 hex digits. The # sign is optional. | default 'ffffff' |
| amount | FLOAT | yes | 0 gives the first colour, 1 gives the second, 0.5 the middle. | 0.0 to 1.0, step 0.01, default 0.5 |

Outputs: `STRING`, `INT`, `INT`, `INT`
