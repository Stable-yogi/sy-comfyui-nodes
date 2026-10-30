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
