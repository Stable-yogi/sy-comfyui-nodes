# Prompt Enhance Request SY (`SYPromptEnhanceRequest`)

Source: `nodes/sy_prompt_enhance_request.py`

**What it does:** Wraps a short idea in a clear request for an LLM, with length and style choices. It only builds the text. Can add an avoid list and ask for a second Negative line. An info line sums up the request.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| idea | STRING | yes | Your short idea, for example: a fox in the snow. | default '', multiline |
| length | COMBO | yes | How long the finished prompt should be. | one of: short, medium, long |
| style | COMBO | yes | The look the finished prompt should describe. | one of: photo, cinematic, anime, painting, 3d render, product shot, any style, watercolor, line art, pixel art, fantasy art |
| output_format | COMBO | yes | A flowing paragraph or short comma phrases. | one of: one paragraph, comma phrases, bullet points |
| notes | STRING | no | Extra wishes, for example: no people, warm colours. | default '', multiline |
| avoid | STRING | no | Things the finished prompt must not contain, for example: text, hands. | default '' |
| also_negative | BOOLEAN | no | On: ask for a second line that starts with Negative: and lists what to avoid. | default False |

Outputs: `STRING`, `STRING`

## How to use

1. Type a short idea in idea, for example a fox in the snow.
2. Choose length, style and output_format. Add extra wishes in notes and things to avoid in avoid. Turn also_negative on to ask for a second line that starts with Negative:.
3. The request output is a clear text you send to a text-writing helper of your choice. This node only builds the text and does not call anything.
The info output sums up the request.
