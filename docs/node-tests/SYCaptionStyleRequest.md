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

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'Look at the attached image and write a caption. Write one short sentence of a...' |
| 2 | style = 'detailed' | PASS | STRING=str 'Look at the attached image and write a caption. Write a detailed description ...' |
| 3 | style = 'tags' | PASS | STRING=str 'Look at the attached image and write a caption. Write a comma separated list ...' |
| 4 | style = 'training caption' | PASS | STRING=str 'Look at the attached image and write a caption. Write one plain caption for m...' |
| 5 | max_words = 2000 (max) | PASS | STRING=str 'Look at the attached image and write a caption. Write one short sentence of a...' |
| 6 | max_words = 1000 (mid) | PASS | STRING=str 'Look at the attached image and write a caption. Write one short sentence of a...' |
| 7 | trigger_word = '' (empty) | PASS | STRING=str 'Look at the attached image and write a caption. Write one short sentence of a...' |
| 8 | subject_hint = '' (empty) | PASS | STRING=str 'Look at the attached image and write a caption. Write one short sentence of a...' |
| 9 | notes = '' (empty) | PASS | STRING=str 'Look at the attached image and write a caption. Write one short sentence of a...' |

## Verdict

All 9 cases behaved as expected (9 passed, 0 rejected with a clear message).
