# System Prompt Presets SY (`SYSystemPromptPresets`)

Source: `nodes/sy_system_prompt_presets.py`

**What it does:** Gives a ready-made system prompt for an LLM node. Type your own text in custom and it replaces the choice. Can add a no-chatter rule (no greetings or code fences), a reply language and your own extra rules.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | Which ready-made system prompt to use. | one of: prompt enhancer, caption writer, translator, summariser, tag generator, negative prompt writer, story writer, video prompt writer, proofreader, idea brainstormer, json formatter, friendly helper |
| custom | STRING | no | Your own system prompt. If not empty it replaces the preset. | default '', multiline |
| no_chatter | BOOLEAN | no | On: tell the model to skip greetings, explanations and code fences. | default False |
| reply_language | STRING | no | Language of the answer, for example 'English' or 'German'. Empty adds nothing. | default '' |
| extra_rules | STRING | no | Your own extra lines, added after the preset, for example 'Keep it under 50 words.' | default '', multiline |

Outputs: `STRING`, `STRING`

## How to use

1. Pick a preset, for example prompt enhancer or caption writer.
2. Or type your own text in custom. If it is not empty it replaces the preset.
3. Optional: turn on no_chatter, set reply_language (for example German) and add extra_rules.
4. Connect system_prompt to the system prompt input of your LLM node.
