# Text Contains SY (`SYTextContains`)

Source: `nodes/sy_text_contains.py`

**What it does:** Checks if a text contains a word or phrase. Gives true or false, and passes the text through. Can look for whole words only, or check a list of words (any or all) and the info line says which were found and which are missing.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to look in. It also comes out unchanged. | default '', multiline |
| needle | STRING | yes | The word or phrase to look for. | default '' |
| case_sensitive | BOOLEAN | yes | On: upper and lower case must match exactly. | default False |
| whole_word | BOOLEAN | no | On: 'cat' is not found inside 'concatenate', only as a word of its own. | default False |
| match | COMBO | no | Use the lines of needle as separate words: true if any, or only if all, are in the text. | one of: the whole phrase, any of the lines, all of the lines |

Outputs: `BOOLEAN`, `STRING`, `STRING`

## How to use

1. Connect the text and type the needle (word or phrase).
2. Turn on case_sensitive or whole_word if needed.
3. To check several words, put one per line in needle and set match to any of the lines or all of the lines.
4. Outputs: true or false, the text unchanged and an info line listing found and missing words.
