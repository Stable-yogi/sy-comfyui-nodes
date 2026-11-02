# Escape Text SY (`SYEscapeText`)

Source: `nodes/sy_escape_text.py`

**What it does:** Makes text safe to paste somewhere else (a JSON string, a web address, one line, or web page text), or turns it back. Broken text to unescape stops with a plain message.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to change. | default '', multiline |
| mode | COMBO | yes | Where the text will be pasted. Single line shows line breaks as \n. | one of: json string, url, single line, html |
| direction | COMBO | yes | Escape makes it safe. Unescape turns it back to normal text. | one of: escape, unescape |

Outputs: `STRING`

## How to use

1. Connect or type the text in **text**.
2. Pick **mode** for where it will be pasted: json string, url, single line or html.
3. Pick **direction**: escape makes it safe, unescape turns it back to normal text.
4. The output **text** is the changed text. If text to unescape is broken, you get a plain message instead.
