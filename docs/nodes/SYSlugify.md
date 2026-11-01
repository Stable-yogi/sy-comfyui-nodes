# Slugify SY (`SYSlugify`)

Source: `nodes/sy_slugify.py`

**What it does:** Turns any text into a simple name made of letters, digits and one separator. Accents are removed. A fallback name stops empty results, windows_safe avoids names like con or nul, and the info line says what was dropped.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to turn into a simple name, for example a title. | default '' |
| separator | COMBO | yes | The character placed between words. | one of: -, _ |
| max_length | INT | yes | Longest result in characters. 0 means no limit. | 0 to 255, step 1, default 0 |
| lowercase | BOOLEAN | yes | On makes every letter small. | default True |
| fallback | STRING | no | Used when nothing is left, for example only Chinese or emoji. Try 'untitled'. | default '' |
| windows_safe | BOOLEAN | no | On: names Windows cannot use (con, nul, com1) get '-file' added. | default False |

Outputs: `STRING`, `STRING`

## How to use

1. Connect the text, for example a title.
2. Pick the separator (- or _), turn lowercase on or off, and set max_length (0 means no limit).
3. Set a fallback name such as untitled for texts that leave nothing. Turn on windows_safe to avoid names such as con or nul.
4. The simple name comes out on slug. The info line says what was dropped.
