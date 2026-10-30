# Prompt Style Templates SY (`SYPromptStyleTemplates`)

Source: `nodes/sy_prompt_style_templates.py`

**What it does:** Pick one of 12 style presets (or none). Adds words before and after your prompt and gives a matching negative prompt.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| text | STRING | yes | Your own prompt. The style words go around it. | default '', multiline |
| style | COMBO | yes | The style preset to use. 'none' leaves the prompt as it is. | one of: none, photo, cinematic, portrait, anime, watercolor, oil painting, pixel art, 3d render, line art, fantasy, sci-fi ... |
| extra_negative | STRING | no | Your own negative words, added after the preset negative. | default '', multiline |

Outputs: `STRING`, `STRING`
