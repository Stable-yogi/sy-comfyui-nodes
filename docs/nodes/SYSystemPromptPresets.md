# System Prompt Presets SY (`SYSystemPromptPresets`)

Source: `nodes/sy_system_prompt_presets.py`

**What it does:** Gives a ready-made system prompt for an LLM node. Type your own text in custom and it replaces the choice.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | Which ready-made system prompt to use. | one of: prompt enhancer, caption writer, translator, summariser, tag generator, negative prompt writer, story writer, video prompt writer, proofreader, idea brainstormer, json formatter, friendly helper |
| custom | STRING | no | Your own system prompt. If not empty it replaces the preset. | default '', multiline |

Outputs: `STRING`
