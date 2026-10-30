# Chat Prompt Builder SY (`SYChatPromptBuilder`)

Source: `nodes/sy_chat_prompt_builder.py`

**What it does:** Joins a system text, a user text and an optional assistant text into one text for any LLM node. It does not call an LLM.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| system | STRING | yes | Standing instructions for the model. Can be empty. | default '', multiline |
| user | STRING | yes | What you ask the model. Must not be empty. | default '', multiline |
| style | COMBO | yes | plain labels, chat tags, or a JSON list of messages. | one of: plain, chat tags, json messages |
| assistant | STRING | no | Optional start of the answer, to steer the model. | default '', multiline |

Outputs: `STRING`
