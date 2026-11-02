# Text Redact SY (`SYTextRedact`)

Source: `nodes/sy_text_redact.py`

**What it does:** Hides chosen words or phrases, and optionally emails, phone-like numbers and web links, before you share a text. The patterns are simple, so read the result. Nothing is sent anywhere.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to clean before sharing it. | default '', multiline |
| words | STRING | yes | Words or phrases to hide, one per line. Blank lines are skipped. | default '', multiline |
| also_hide | COMBO | yes | Also hide email addresses, phone-like numbers or web links. The patterns are simple, not perfect. | one of: nothing, email addresses, phone-like numbers, web links, all of these |
| replace_with | COMBO | yes | What goes in place of hidden text. Block characters have a fixed size, stars keep the length. | one of: block characters, [REDACTED], same length stars, custom |
| custom | STRING | yes | The text used when replace_with is custom. | default '***' |
| whole_words_only | BOOLEAN | yes | On: Ann does not hide the start of Annual. Off: any match is hidden. | default True |
| ignore_case | BOOLEAN | yes | On: ann also matches Ann and ANN. | default True |

Outputs: `STRING`, `INT`

## How to use

1. Connect the text to **text**.
2. Type the names or phrases to hide in **words**, one per line.
3. Pick **also_hide** for emails, phone-like numbers or links.
4. Choose what replaces them in **replace_with**.
5. Read the result before you share it; **hidden_count** says how many pieces were hidden.
