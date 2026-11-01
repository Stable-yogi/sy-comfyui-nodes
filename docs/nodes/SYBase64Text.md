# Base64 Text SY (`SYBase64Text`)

Source: `nodes/sy_base64_text.py`

**What it does:** Turns a text into base64 code, or base64 code back into text. Decoding forgives missing padding, line breaks and a pasted 'data:...;base64,' start, and a bad code gives one plain sentence. Also gives an info line.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to encode, or the base64 code to decode. | default '', multiline |
| mode | COMBO | yes | encode makes base64 code; decode turns it back into text. | one of: encode, decode |
| url_safe | BOOLEAN | yes | On: use the web-address-safe letters (- and _ instead of + and /). | default False |

Outputs: `STRING`, `STRING`

## How to use

1. Put the text in text.
2. Set mode to encode to make base64 code, or decode to turn base64 code back into text.
3. Turn on url_safe to use web-address-safe letters.
4. Decoding forgives missing padding, line breaks and a pasted data:...;base64, start. A bad code gives one plain sentence.
