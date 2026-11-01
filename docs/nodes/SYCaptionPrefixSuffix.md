# Caption Prefix Suffix SY (`SYCaptionPrefixSuffix`)

Source: `nodes/sy_caption_prefix_suffix.py`

**What it does:** Adds a trigger word before and/or after a caption, one caption or one per line. Skips it when the caption already starts or ends with it (any capital letters). Can also tidy stray spaces and commas, and an info line says how many captions were changed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| caption | STRING | yes | The caption text. Several captions can be given, one per line. | default '', multiline |
| prefix | STRING | yes | Trigger word or phrase to put first. Leave empty for none. | default '' |
| suffix | STRING | yes | Trigger word or phrase to put last. Leave empty for none. | default '' |
| separator | STRING | yes | Text placed between the trigger word and the caption. | default ', ' |
| per_line | BOOLEAN | yes | On: treat every line as its own caption. Off: the whole text is one caption. | default False |
| tidy | BOOLEAN | no | On: first squeeze double spaces, spaces before commas and doubled commas. | default False |

Outputs: `STRING`, `STRING`

## How to use

1. Put your caption in caption. Turn on per_line to treat every line as its own caption.
2. Fill prefix and/or suffix with the trigger word. separator goes between it and the caption.
3. It skips a trigger word the caption already starts or ends with.
4. Turn on tidy to squeeze double spaces and stray commas first. The new caption comes out, and info says how many were changed.
