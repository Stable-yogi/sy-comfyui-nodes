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

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str 'blurry, low quality, jpeg artifacts, watermark, text, logo, signature, croppe...' |
| 2 | preset = 'photo realism' | PASS | STRING=str 'cartoon, illustration, painting, drawing, plastic skin, oversaturated, overex...' |
| 3 | preset = 'portrait' | PASS | STRING=str 'bad anatomy, deformed face, asymmetrical eyes, extra fingers, missing fingers...' |
| 4 | preset = 'full body' | PASS | STRING=str 'bad anatomy, extra limbs, missing limbs, long neck, disfigured, bad proportio...' |
| 5 | preset = 'anime' | PASS | STRING=str 'photo, realistic, 3d render, lowres, bad anatomy, bad hands, extra digits, jp...' |
| 6 | preset = 'landscape' | PASS | STRING=str 'people, text, watermark, oversaturated, blurry, lowres, distorted horizon, no...' |
| 7 | preset = 'product shot' | PASS | STRING=str 'dirty, scratches, fingerprints, harsh shadows, cluttered background, blurry, ...' |
| 8 | preset = 'architecture' | PASS | STRING=str 'distorted lines, warped perspective, people, cars, text, watermark, blurry, l...' |
| 9 | preset = 'painting' | PASS | STRING=str 'photo, 3d render, digital noise, blurry, muddy colours, text, watermark, sign...' |
| 10 | preset = 'minimal' | PASS | STRING=str 'blurry, lowres, watermark' |
| 11 | mode = 'replace preset' | REJECTED | ValueError: mode is 'replace preset' but custom is empty: write your text or switch the mode |
| 12 | custom = '' (empty) | PASS | STRING=str 'blurry, low quality, jpeg artifacts, watermark, text, logo, signature, croppe...' |

## Verdict

All 12 cases behaved as expected (11 passed, 1 rejected with a clear message).
