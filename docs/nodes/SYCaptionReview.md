# Caption Review SY (`SYCaptionReview`)

Source: `nodes/sy_caption_review.py`

**What it does:** Reviews one caption for training: too short or long, words repeated too often, words you banned. Gives true or false and a report.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| caption | STRING | yes | The caption to review. | default '', multiline |
| min_words | INT | yes | Fewer words than this counts as too short. | 0 to 1000, default 5 |
| max_words | INT | yes | More words than this counts as too long. | 1 to 1000, default 75 |
| max_repeat | INT | yes | How often one word may appear. Small words like the and of are ignored. | 1 to 100, default 3 |
| banned_words | STRING | yes | Words or phrases that must not appear. Separate with commas or new lines. | default '', multiline |

Outputs: `BOOLEAN`, `STRING`
