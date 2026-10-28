# System Prompt Presets SY (`SYSystemPromptPresets`)

Source: `nodes/sy_system_prompt_presets.py`

**What it does:** Gives a ready-made system prompt for an LLM node. Type your own text in custom and it replaces the choice.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | Which ready-made system prompt to use. | one of: prompt enhancer, caption writer, translator, summariser, tag generator, negative prompt writer, story writer, video prompt writer, proofreader, idea brainstormer, json formatter, friendly helper |
| custom | STRING | no | Your own system prompt. If not empty it replaces the preset. | default '', multiline |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'You rewrite short image ideas into one rich, concrete image prompt. Describe ...' |
| 2 | preset = 'caption writer' | PASS | STRING=str 'You describe pictures in plain, accurate sentences. Say only what is visible....' |
| 3 | preset = 'translator' | PASS | STRING=str "You translate the user's text into English. Keep the meaning, tone and any na..." |
| 4 | preset = 'summariser' | PASS | STRING=str "You summarise the user's text in a few clear sentences. Keep the key facts an..." |
| 5 | preset = 'tag generator' | PASS | STRING=str "You turn the user's text into a comma separated list of short lowercase tags...." |
| 6 | preset = 'negative prompt writer' | PASS | STRING=str 'You write a negative prompt for an image model. List flaws to avoid as short ...' |
| 7 | preset = 'story writer' | PASS | STRING=str "You write a short story scene from the user's idea. Use simple vivid words. R..." |
| 8 | preset = 'video prompt writer' | PASS | STRING=str "You turn the user's idea into a video prompt. Describe the subject, the actio..." |
| 9 | preset = 'proofreader' | PASS | STRING=str "You fix spelling, grammar and punctuation in the user's text. Keep the voice ..." |
| 10 | preset = 'idea brainstormer' | PASS | STRING=str "You give ten short, different ideas for the user's topic as a numbered list. ..." |
| 11 | preset = 'json formatter' | PASS | STRING=str "You turn the user's text into valid JSON. Use clear key names. Reply with the..." |
| 12 | preset = 'friendly helper' | PASS | STRING=str 'You are a friendly helper. Answer in plain words, be short and be honest when...' |
| 13 | custom = '' (empty) | PASS | STRING=str 'You rewrite short image ideas into one rich, concrete image prompt. Describe ...' |

## Verdict

All 13 cases behaved as expected (13 passed, 0 rejected with a clear message).
