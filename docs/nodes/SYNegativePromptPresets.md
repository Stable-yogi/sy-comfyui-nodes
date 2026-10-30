# Negative Prompt Presets SY (`SYNegativePromptPresets`)

Source: `nodes/sy_negative_prompt_presets.py`

**What it does:** Gives a ready-made negative prompt for an image model. Add your own words after it, or replace it.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | Which ready-made negative prompt to use. | one of: general clean, photo realism, portrait, full body, anime, landscape, product shot, architecture, painting, minimal |
| mode | COMBO | yes | Put your custom words after the preset, or use them instead. | one of: add after preset, replace preset |
| custom | STRING | no | Your own words to avoid, separated by commas. | default '', multiline |

Outputs: `STRING`
