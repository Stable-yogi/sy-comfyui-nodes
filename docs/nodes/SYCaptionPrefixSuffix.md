# Caption Prefix Suffix SY (`SYCaptionPrefixSuffix`)

Source: `nodes/sy_caption_prefix_suffix.py`

**What it does:** Adds a trigger word before and/or after a caption. Skips it when the caption already starts or ends with it.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| caption | STRING | yes | The caption text. Several captions can be given, one per line. | default '', multiline |
| prefix | STRING | yes | Trigger word or phrase to put first. Leave empty for none. | default '' |
| suffix | STRING | yes | Trigger word or phrase to put last. Leave empty for none. | default '' |
| separator | STRING | yes | Text placed between the trigger word and the caption. | default ', ' |
| per_line | BOOLEAN | yes | On: treat every line as its own caption. Off: the whole text is one caption. | default False |

Outputs: `STRING`
