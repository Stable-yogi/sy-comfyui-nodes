# Strip Markdown SY (`SYStripMarkdown`)

Source: `nodes/sy_strip_markdown.py`

**What it does:** Turns reply text with markdown marks (stars, hashes, backticks, bullets, links) into clean plain text. Words inside code are kept.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text that has markdown marks in it. | default '', multiline |
| keep_bullets | BOOLEAN | yes | On: list lines keep a plain dash in front. Off: the dash is removed. | default False |
| keep_link_text | BOOLEAN | yes | On: a link becomes its label. Off: links are dropped completely. | default True |

Outputs: `STRING`

## How to use

1. Connect the text with markdown marks to **text**.
2. Turn on **keep_bullets** if list lines should keep a plain dash.
3. Leave **keep_link_text** on to keep a link's label, or turn it off to drop links completely.
4. The output **text** is clean plain text.
