# Prompt Sections SY (`SYPromptSections`)

Source: `nodes/sy_prompt_sections.py`

**What it does:** Joins prompt parts (subject, setting, lighting, camera, style, extra) into one prompt. Empty parts are skipped.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| join_with | STRING | yes | The text put between the parts. Use a comma, or a new line. | default ', ' |
| label_mode | COMBO | yes | label_colon puts a name before each part, like 'Lighting: soft'. | one of: none, label_colon |
| subject | STRING | no | Who or what the picture shows. | default '', multiline |
| setting | STRING | no | Where it happens: place, time, weather. | default '', multiline |
| lighting | STRING | no | The light: soft, golden hour, neon and so on. | default '', multiline |
| camera | STRING | no | Camera, lens and angle. | default '', multiline |
| style | STRING | no | The look: painting, photo, anime and so on. | default '', multiline |
| extra | STRING | no | Anything else you want to add at the end. | default '', multiline |

Outputs: `STRING`, `INT`
