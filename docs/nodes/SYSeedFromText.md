# Seed From Text SY (`SYSeedFromText`)

Source: `nodes/sy_seed_from_text.py`

**What it does:** Turns any text into a seed number. The same text and salt always give the same seed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Any text, such as a name or a prompt. Empty text is allowed. | default '' |
| salt | INT | yes | Change this number to get a different seed from the same text. | 0 to 4294967295, step 1, default 0 |

Outputs: `INT`
