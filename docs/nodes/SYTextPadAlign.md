# Text Pad Align SY (`SYTextPadAlign`)

Source: `nodes/sy_text_pad_align.py`

**What it does:** Makes all lines of a text the same width by padding them with a fill character. Align the text left, right or centre. Optionally cut lines that are too long.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to pad. Each line is padded on its own. | default '', multiline |
| align | COMBO | yes | Where the words sit inside the width. Centre puts the extra space on the right. | one of: left, right, centre |
| width | INT | yes | Characters per line. 0 uses the longest line. | 0 to 500, default 0 |
| fill | STRING | yes | The one character used for padding. A space by default. | default ' ' |
| truncate | BOOLEAN | yes | On: cut lines longer than the width. Off: keep them whole. | default False |

Outputs: `STRING`, `INT`

## How to use

1. Paste the lines into **text**.
2. Pick **align**.
3. Set **width**, or leave 0 to match the longest line.
4. Type one character in **fill** (a space is fine). Anything other than one character stops with a message.
5. Turn on **truncate** if long lines must be cut to the width.
