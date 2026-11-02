# Humanize Number SY (`SYHumanizeNumber`)

Source: `nodes/sy_humanize_number.py`

**What it does:** Shows a big raw number the way people read it: file sizes (1.5 GB), durations (1 h 02 min 05 s) or counts (12.3 k).

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | FLOAT | yes | The raw number to show. | -1000000000000000.0 to 1000000000000000.0, step 1.0, default 0.0 |
| kind | COMBO | yes | What the number counts: bytes of a file, seconds of time, or plain things. | one of: bytes, seconds, count |
| decimals | INT | yes | How many digits after the dot for big numbers. | 0 to 4, default 1 |

Outputs: `STRING`

## How to use

1. Connect or type the raw number in **value**.
2. Pick **kind**: bytes for file sizes, seconds for durations, count for plain things.
3. Set **decimals** for digits after the dot on big numbers.
4. The output **text** is the easy-to-read form, such as 1.5 GB.
