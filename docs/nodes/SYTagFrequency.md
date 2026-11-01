# Tag Frequency SY (`SYTagFrequency`)

Source: `nodes/sy_tag_frequency.py`

**What it does:** Counts how many captions use each tag and lists them from the most common to the rarest. Also checks the captions for training mistakes: a tag twice in one caption, a trigger word that is missing or not first, and banned words.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| captions | STRING | yes | All captions, one caption per line. | default '', multiline |
| separator | STRING | yes | The character that splits one tag from the next. Usually a comma. | default ',' |
| lowercase | BOOLEAN | yes | On: Dog and dog count as the same tag. | default True |
| min_count | INT | yes | Hide tags that appear in fewer captions than this. | 1 to 1000000, default 1 |
| top_n | INT | yes | Show only the most common tags. 0 shows all of them. | 0 to 100000, default 0 |
| trigger_word | STRING | no | Your LoRA trigger word, for example 'ohwx'. Every caption should start with it. Empty skips this check. | default '' |
| banned_words | STRING | no | Words that must not appear in any caption, separated by commas, for example 'watermark, text'. | default '', multiline |

Outputs: `STRING`, `INT`, `STRING`, `INT`

## How to use

1. Paste all captions into captions, one caption per line.
2. Set separator (usually a comma), lowercase, min_count and top_n (0 shows all tags).
3. Optional: type your trigger_word to check it is first in every caption, and list banned_words.
4. Outputs: the tag list from most to least common, the number of unique tags, a list of problems and the problem count.
