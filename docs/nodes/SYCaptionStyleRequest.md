# Caption Style Request SY (`SYCaptionStyleRequest`)

Source: `nodes/sy_caption_style_request.py`

**What it does:** Builds a request that asks an LLM to caption an image: short, detailed, tags or training caption. It only builds the text.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| style | COMBO | yes | What kind of caption you want back. | one of: short, detailed, tags, training caption |
| max_words | INT | yes | Word limit for the caption. 0 uses a sensible limit for the style. | 0 to 2000, default 0 |
| trigger_word | STRING | no | A word the caption must start with, often used in training. | default '' |
| subject_hint | STRING | no | What the image shows, if you know it. Helps the model. | default '' |
| notes | STRING | no | Extra wishes, for example: mention the background. | default '', multiline |

Outputs: `STRING`
