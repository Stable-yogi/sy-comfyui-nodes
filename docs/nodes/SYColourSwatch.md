# Colour Swatch SY (`SYColourSwatch`)

Source: `nodes/sy_colour_swatch.py`

**What it does:** Reads a colour code (like d4a537), gives red, green and blue numbers, a clean code, a small colour picture and an info line that says if black or white text reads best on it.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| colour | STRING | yes | A hex colour: 3 or 6 digits, with or without the # sign. | default 'd4a537' |

Outputs: `INT`, `INT`, `INT`, `STRING`, `IMAGE`, `STRING`

## How to use

1. Type a colour code such as d4a537 in colour.
2. Outputs: r, g and b numbers, a clean hex code, a small swatch picture.
3. The info line says if black or white text reads best on it.
