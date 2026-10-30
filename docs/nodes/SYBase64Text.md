# Base64 Text SY (`SYBase64Text`)

Source: `nodes/sy_base64_text.py`

**What it does:** Turns a text into base64 code, or turns base64 code back into the text.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to encode, or the base64 code to decode. | default '', multiline |
| mode | COMBO | yes | encode makes base64 code; decode turns it back into text. | one of: encode, decode |
| url_safe | BOOLEAN | yes | On: use the web-address-safe letters (- and _ instead of + and /). | default False |

Outputs: `STRING`
