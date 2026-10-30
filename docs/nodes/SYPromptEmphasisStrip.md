# Prompt Emphasis Strip SY (`SYPromptEmphasisStrip`)

Source: `nodes/sy_prompt_emphasis_strip.py`

**What it does:** Removes emphasis marks from a prompt: (word:1.2), ((word)) and [word] become word. Can also remove LoRA tags and BREAK.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | The prompt you want to clean. | default '', multiline |
| remove_lora_tags | BOOLEAN | yes | On: also remove tags like <lora:name:0.8>. | default False |
| remove_break | BOOLEAN | yes | On: also remove the word BREAK when it stands alone. | default False |

Outputs: `STRING`
