# Text Similarity SY (`SYTextSimilarity`)

Source: `nodes/sy_text_similarity.py`

**What it does:** Tells how alike two texts are, from 0 (nothing in common) to 1 (the same). Use it to see if a prompt changed much or a caption repeats.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text_a | STRING | yes | The first text. | default '', multiline |
| text_b | STRING | yes | The second text. | default '', multiline |
| compare_by | COMBO | yes | Compare whole words, or single letters. | one of: words, characters |
| ignore_case | BOOLEAN | yes | On: capital and small letters count as the same. | default True |
| threshold | FLOAT | yes | is_close is true when the similarity is at least this. | 0.0 to 1.0, step 0.01, default 0.8 |

Outputs: `FLOAT`, `BOOLEAN`

## How to use

1. Connect the two texts to **text_a** and **text_b**.
2. Pick **compare_by**: whole words, or single letters.
3. Leave **ignore_case** on if capitals should not matter.
4. Set **threshold** for what counts as close.
5. The outputs give **similarity** (0 to 1) and **is_close**, true when the similarity reaches the threshold.
