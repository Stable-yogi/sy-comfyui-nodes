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

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str ''; INT=int 0 |
| 2 | join_with = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 3 | label_mode = 'label_colon' | PASS | STRING=str ''; INT=int 0 |
| 4 | subject = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 5 | setting = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 6 | lighting = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 7 | camera = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 8 | style = '' (empty) | PASS | STRING=str ''; INT=int 0 |
| 9 | extra = '' (empty) | PASS | STRING=str ''; INT=int 0 |

## Verdict

All 9 cases behaved as expected (9 passed, 0 rejected with a clear message).
