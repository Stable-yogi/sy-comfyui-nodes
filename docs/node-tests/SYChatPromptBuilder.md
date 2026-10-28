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

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: user text is empty: write what you want to ask |
| 2 | system = '' (empty) | REJECTED | ValueError: user text is empty: write what you want to ask |
| 3 | user = '' (empty) | REJECTED | ValueError: user text is empty: write what you want to ask |
| 4 | style = 'chat tags' | REJECTED | ValueError: user text is empty: write what you want to ask |
| 5 | style = 'json messages' | REJECTED | ValueError: user text is empty: write what you want to ask |
| 6 | assistant = '' (empty) | REJECTED | ValueError: user text is empty: write what you want to ask |

## Verdict

All 6 cases behaved as expected (0 passed, 6 rejected with a clear message).
