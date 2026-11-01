# Repeater SY (`SYRepeater`)

Source: `nodes/sy_repeater.py`

**What it does:** Takes one value and sends the same value out on eight outputs, so one wire does not have to be split by hand.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | * | yes | Any value. It is sent out unchanged on all eight outputs. |  |

Outputs: `*`, `*`, `*`, `*`, `*`, `*`, `*`, `*`

## How to use

1. Connect any value (a number, text, picture, model) to value.
2. Use out_1 to out_8: each one gives the same value, unchanged.
It saves splitting one wire by hand into many.
