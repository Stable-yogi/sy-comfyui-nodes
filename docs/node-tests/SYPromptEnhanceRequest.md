# Prompt Enhance Request SY (`SYPromptEnhanceRequest`)

Source: `nodes/sy_prompt_enhance_request.py`

**What it does:** Wraps a short idea in a clear request for an LLM, with length and style choices. It only builds the text.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| idea | STRING | yes | Your short idea, for example: a fox in the snow. | default '', multiline |
| length | COMBO | yes | How long the finished prompt should be. | one of: short, medium, long |
| style | COMBO | yes | The look the finished prompt should describe. | one of: photo, cinematic, anime, painting, 3d render, product shot, any style |
| output_format | COMBO | yes | A flowing paragraph or short comma phrases. | one of: one paragraph, comma phrases |
| notes | STRING | no | Extra wishes, for example: no people, warm colours. | default '', multiline |

Outputs: `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 2 | idea = '' (empty) | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 3 | length = 'medium' | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 4 | length = 'long' | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 5 | style = 'cinematic' | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 6 | style = 'anime' | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 7 | style = 'painting' | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 8 | style = '3d render' | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 9 | style = 'product shot' | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 10 | style = 'any style' | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 11 | output_format = 'comma phrases' | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |
| 12 | notes = '' (empty) | REJECTED | ValueError: idea is empty: write a short idea such as 'a fox in the snow' |

## Verdict

All 12 cases behaved as expected (0 passed, 12 rejected with a clear message).
