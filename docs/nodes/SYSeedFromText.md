# Seed From Text SY (`SYSeedFromText`)

Source: `nodes/sy_seed_from_text.py`

**What it does:** Turns any text into a seed number. The same text and salt always give the same seed. Turn on ignore_case_spaces so a stray capital letter or extra space does not change the seed. The info line shows the text that was used.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Any text, such as a name or a prompt. Empty text is allowed. | default '' |
| salt | INT | yes | Change this number to get a different seed from the same text. | 0 to 4294967295, step 1, default 0 |
| ignore_case_spaces | BOOLEAN | no | On makes Cat and cat give the same seed. Off keeps the text exactly as typed. | default False |

Outputs: `INT`, `STRING`
