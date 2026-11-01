# LLM Reply Clean SY (`SYLLMReplyClean`)

Source: `nodes/sy_llm_reply_clean.py`

**What it does:** Cleans a chatty text reply: removes the model's <think> notes, code fences, an intro line like 'Here is...:', wrapping quotes, an optional closing 'Let me know...' line and extra blank lines. An info line says what was removed.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The reply text you want to clean. | default '', multiline |
| strip_code_fences | BOOLEAN | yes | On: remove the ``` lines and keep what is inside. | default True |
| strip_preamble | BOOLEAN | yes | On: drop a first line like 'Here is your prompt:' that ends with a colon. | default True |
| strip_wrapping_quotes | BOOLEAN | yes | On: remove quote marks that wrap the whole text. | default True |
| first_paragraph_only | BOOLEAN | yes | On: keep only the first paragraph and drop the rest. | default False |
| collapse_blank_lines | BOOLEAN | yes | On: turn several empty lines in a row into one. | default True |
| strip_thinking | BOOLEAN | no | On: remove the <think>...</think> notes some models write before the answer. | default True |
| strip_closing_note | BOOLEAN | no | On: drop a last line like 'Let me know if you want changes.' | default False |

Outputs: `STRING`, `STRING`
