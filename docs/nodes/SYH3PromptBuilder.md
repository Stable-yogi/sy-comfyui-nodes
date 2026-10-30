# H3PromptBuilder SY (`SYH3PromptBuilder`)

Source: `nodes/sy_h3_prompt_builder.py`

**What it does:** Builds one tidy prompt for a video model from style, world, action, timeline and spoken lines. Warns about mistakes.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| style | STRING | yes | The look of the clip, for example soft film light. | default '', multiline |
| world | STRING | yes | Where the scene happens and who is in it. | default '', multiline |
| action | STRING | yes | What happens in the clip. Write Picture 1, Picture 2 to point at input pictures. | default '', multiline |
| picture_count | INT | yes | How many input pictures you give the video model. | 0 to 4, default 0 |
| dialogue | STRING | no | Spoken lines, one per line. Each line gets its own speech tag. | default '', multiline |
| dialogue_language | STRING | no | Language of the spoken lines, for example Japanese. Leave empty for none. | default '' |
| time_codes | STRING | no | One line per moment, like 0-4s: she turns round. | default '', multiline |

Outputs: `STRING`, `STRING`
