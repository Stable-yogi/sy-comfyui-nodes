# Sentence Pick SY (`SYSentencePick`)

Source: `nodes/sy_sentence_pick.py`

**What it does:** Splits text into sentences and picks the first few, the last few, one by number, or lists them all numbered. Can drop helper chatter such as 'Sure! Here is...' and 'Let me know if...', and the info line says what was taken.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to split into sentences. | default '', multiline |
| mode | COMBO | yes | first_n and last_n take n sentences. index takes one. all_numbered lists all. | one of: first_n, last_n, index, all_numbered |
| n | INT | yes | How many sentences to take in first_n or last_n mode. | 1 to 100000, default 1 |
| index | INT | yes | Which sentence to take in index mode, counting from 0. | 0 to 100000, default 0 |
| skip_chatter | BOOLEAN | no | On: first drop helper lines like 'Sure! Here is the caption:' and 'Let me know if...'. | default False |

Outputs: `STRING`, `INT`, `STRING`

## How to use

1. Connect the text.
2. Pick mode: first_n or last_n take n sentences, index takes one sentence (counting from 0), all_numbered lists every sentence with a number.
3. Turn on skip_chatter to drop helper lines such as "Sure! Here is..." first.
4. Outputs: the picked text, the sentence total and an info line.
