# LLM Reply Clean SY (`SYLLMReplyClean`)

Source: `nodes/sy_llm_reply_clean.py`

**What it does:** Cleans a chatty text reply: removes code fences, an intro line like 'Here is...:', wrapping quotes and extra blank lines.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The reply text you want to clean. | default '', multiline |
| strip_code_fences | BOOLEAN | yes | On: remove the ``` lines and keep what is inside. | default True |
| strip_preamble | BOOLEAN | yes | On: drop a first line like 'Here is your prompt:' that ends with a colon. | default True |
| strip_wrapping_quotes | BOOLEAN | yes | On: remove quote marks that wrap the whole text. | default True |
| first_paragraph_only | BOOLEAN | yes | On: keep only the first paragraph and drop the rest. | default False |
| collapse_blank_lines | BOOLEAN | yes | On: turn several empty lines in a row into one. | default True |

Outputs: `STRING`
