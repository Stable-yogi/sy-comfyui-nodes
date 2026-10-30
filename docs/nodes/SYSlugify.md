# Slugify SY (`SYSlugify`)

Source: `nodes/sy_slugify.py`

**What it does:** Turns any text into a simple name made of letters, digits and one separator. Accents are removed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to turn into a simple name, for example a title. | default '' |
| separator | COMBO | yes | The character placed between words. | one of: -, _ |
| max_length | INT | yes | Longest result in characters. 0 means no limit. | 0 to 255, step 1, default 0 |
| lowercase | BOOLEAN | yes | On makes every letter small. | default True |

Outputs: `STRING`
