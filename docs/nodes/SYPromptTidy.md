# Prompt Tidy SY (`SYPromptTidy`)

Source: `nodes/sy_prompt_tidy.py`

**What it does:** Joins a prompt with extra text and tidies it in one node. Steps run in this order: join, clean spaces and commas, lowercase, remove listed tags, remove duplicates (keeps the strongest weight), weights (keep, strip or round to 1 decimal), trigger words first, cut whole tags from the end to fit a token limit. Token counts are only about right. Tag steps treat the prompt as a comma list. Info says what changed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt to tidy. | default '', multiline |
| extra_text | STRING | no | Added after the text. Empty means nothing is added. | default '', multiline |
| separator | COMBO | no | What goes between the text and the extra text. | one of: comma, new line, space, period |
| clean | BOOLEAN | no | On: remove stray spaces, doubled commas and a trailing comma. | default True |
| remove_duplicates | BOOLEAN | no | On: a tag written twice stays once, with the strongest weight. | default False |
| weights | COMBO | no | Keep the (word:1.2) weights, strip them all, or round them to 1 decimal. | one of: keep, strip all, normalise to 1 decimal |
| lowercase | BOOLEAN | no | On: write the prompt in lowercase. <lora:...> tags stay as they are. | default False |
| trigger_words | STRING | no | Words to put first, separated by commas. Not repeated. | default '' |
| remove_words | STRING | no | Whole tags to remove, separated by commas. Case and weights are ignored. | default '' |
| max_tokens | INT | no | 0 = no limit. Otherwise whole tags are cut from the end to fit. | 0 to 4096, default 0 |
| token_style | COMBO | no | How tokens are guessed. Both are rough. | one of: words*1.3 estimate, characters/4 estimate |
| enabled | BOOLEAN | no | Off: the text passes through unchanged. | default True |

Outputs: `STRING`, `INT`, `STRING`

## How to use

1. Put your prompt in text. Add more in extra_text and pick how they are joined in separator.
2. Switch on the steps you need: clean, remove_duplicates, lowercase, weights (keep, strip all or round to 1 decimal), trigger_words (put first), remove_words, and max_tokens (0 is no limit).
3. They run in a fixed order. Token counts are only about right. Turn enabled off to pass the text through unchanged.
Outputs: the text, a token estimate and an info line.
