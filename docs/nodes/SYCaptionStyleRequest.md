# Caption Style Request SY (`SYCaptionStyleRequest`)

Source: `nodes/sy_caption_style_request.py`

**What it does:** Builds a request that asks an LLM to caption an image: short, detailed, tags or training caption, with an optional trigger word and a list of words it must not use. An info line gives the word limit. It only builds the text.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| style | COMBO | yes | What kind of caption you want back. | one of: short, detailed, tags, training caption |
| max_words | INT | yes | Word limit for the caption. 0 uses a sensible limit for the style. | 0 to 2000, default 0 |
| trigger_word | STRING | no | A word the caption must start with, often used in training. | default '' |
| subject_hint | STRING | no | What the image shows, if you know it. Helps the model. | default '' |
| notes | STRING | no | Extra wishes, for example: mention the background. | default '', multiline |
| avoid_words | STRING | no | Words the caption must not use, separated by commas, for example: beautiful, stunning. | default '' |

Outputs: `STRING`, `STRING`

## How to use

1. Pick style: short, detailed, tags or training caption.
2. Optionally set max_words (0 uses a sensible limit), trigger_word, subject_hint, notes and avoid_words.
3. The text comes out as request. Send it to an LLM node. This node only builds the text.
