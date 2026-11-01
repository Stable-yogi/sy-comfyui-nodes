# Text Truncate SY (`SYTextTruncate`)

Source: `nodes/sy_text_truncate.py`

**What it does:** Shortens a text to a maximum length and adds an ending such as three dots. Can cut at a word end, or keep both ends and cut the middle (good for long file names). The info line says how much was removed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to shorten. | default '', multiline |
| max_chars | INT | yes | Longest allowed result, counting the ending. | 1 to 100000, default 100 |
| suffix | STRING | yes | Added at the end when the text was cut. Leave empty for none. | default '...' |
| at_word | BOOLEAN | yes | On: cut back to the end of a whole word. Off: cut at the exact character. | default True |
| cut_from | COMBO | no | End keeps the start. Middle keeps both ends and puts the ending in the middle. at_word is ignored for middle. | one of: end (keep the start), middle (keep both ends) |

Outputs: `STRING`, `BOOLEAN`, `STRING`

## How to use

1. Connect the text and set max_chars (the ending counts too).
2. Set suffix, for example three dots. Leave it empty for none.
3. Turn on at_word to cut at the end of a whole word.
4. Set cut_from to middle to keep both ends and cut the centre, good for long file names. Outputs: the text, truncated true or false, and an info line.
