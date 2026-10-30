# Sentence Pick SY (`SYSentencePick`)

Source: `nodes/sy_sentence_pick.py`

**What it does:** Splits text into sentences and picks the first few, the last few, one by number, or lists them all numbered.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The text to split into sentences. | default '', multiline |
| mode | COMBO | yes | first_n and last_n take n sentences. index takes one. all_numbered lists all. | one of: first_n, last_n, index, all_numbered |
| n | INT | yes | How many sentences to take in first_n or last_n mode. | 1 to 100000, default 1 |
| index | INT | yes | Which sentence to take in index mode, counting from 0. | 0 to 100000, default 0 |

Outputs: `STRING`, `INT`
