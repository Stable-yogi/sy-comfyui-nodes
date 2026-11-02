# Colour Contrast Check SY (`SYColourContrastCheck`)

Source: `nodes/sy_colour_contrast_check.py`

**What it does:** Tells whether text in one colour is easy to read on another colour, for thumbnails and overlays. Also names black or white as the better text colour for that background.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| foreground | STRING | yes | The text colour as web hex. | default '#ffffff' |
| background | STRING | yes | The colour behind the text, as web hex. | default '#3366cc' |

Outputs: `FLOAT`, `STRING`, `STRING`

## How to use

1. Type the text colour in **foreground** as a web colour.
2. Type the colour behind the text in **background**.
3. The outputs give the contrast **ratio** (higher is easier to read), a **grade** for it, and **better_text_colour**, black or white, for that background.
