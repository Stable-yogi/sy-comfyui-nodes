# Caption Review SY (`SYCaptionReview`)

Source: `nodes/sy_caption_review.py`

**What it does:** Reviews one caption for training: too short or long, words repeated too often, words you banned. Can also check that the trigger word comes first and that must-have words are there. Gives true or false, a report and the word count.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| caption | STRING | yes | The caption to review. | default '', multiline |
| min_words | INT | yes | Fewer words than this counts as too short. | 0 to 1000, default 5 |
| max_words | INT | yes | More words than this counts as too long. | 1 to 1000, default 75 |
| max_repeat | INT | yes | How often one word may appear. Small words like the and of are ignored. | 1 to 100, default 3 |
| banned_words | STRING | yes | Words or phrases that must not appear. Separate with commas or new lines. | default '', multiline |
| must_start_with | STRING | no | Trigger word the caption must begin with, for example sks_dog. Empty skips the check. | default '' |
| must_include | STRING | no | Words that must appear, separated by commas or new lines. | default '', multiline |

Outputs: `BOOLEAN`, `STRING`, `INT`

## How to use

1. Put the caption in caption.
2. Set min_words, max_words and max_repeat (how often one word may appear; small words are ignored).
3. List banned_words, and optionally must_start_with (a trigger word) and must_include.
4. Outputs: ok (true or false), a report, and word_count.
