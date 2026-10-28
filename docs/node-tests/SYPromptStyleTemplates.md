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

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | STRING=str ''; STRING=str '' |
| 2 | text = '' (empty) | PASS | STRING=str ''; STRING=str '' |
| 3 | style = 'photo' | PASS | STRING=str 'photo of, natural light, sharp focus, realistic skin texture, 35mm'; STRING=str 'cartoon, painting, illustration, blurry, lowres' |
| 4 | style = 'cinematic' | PASS | STRING=str 'cinematic still of, dramatic lighting, shallow depth of field, film grain, an...'; STRING=str 'flat lighting, cartoon, lowres, oversaturated' |
| 5 | style = 'portrait' | PASS | STRING=str 'studio portrait of, soft key light, detailed eyes, 85mm lens, bokeh background'; STRING=str 'deformed face, extra fingers, blurry, lowres' |
| 6 | style = 'anime' | PASS | STRING=str 'anime illustration of, clean line art, vibrant colors, detailed background'; STRING=str 'photo, realistic, 3d render, lowres, bad anatomy' |
| 7 | style = 'watercolor' | PASS | STRING=str 'watercolor painting of, soft washes, paper texture, loose brush strokes'; STRING=str 'photo, sharp edges, digital look, lowres' |
| 8 | style = 'oil painting' | PASS | STRING=str 'oil painting of, visible brush strokes, rich colors, canvas texture'; STRING=str 'photo, flat colors, digital look, blurry' |
| 9 | style = 'pixel art' | PASS | STRING=str 'pixel art of, 16-bit, limited palette, crisp pixels'; STRING=str 'blurry, smooth gradients, photo, anti-aliasing' |
| 10 | style = '3d render' | PASS | STRING=str '3d render of, octane render, soft studio lighting, detailed materials'; STRING=str 'painting, sketch, lowres, noisy' |
| 11 | style = 'line art' | PASS | STRING=str 'black and white line art of, clean ink lines, white background, high contrast'; STRING=str 'color, shading, photo, blurry' |
| 12 | style = 'fantasy' | PASS | STRING=str 'fantasy artwork of, epic scene, magical atmosphere, intricate details, golden...'; STRING=str 'modern, photo, lowres, blurry' |
| 13 | style = 'sci-fi' | PASS | STRING=str 'science fiction concept art of, futuristic, neon accents, volumetric light, d...'; STRING=str 'medieval, countryside, lowres, blurry' |
| 14 | style = 'product shot' | PASS | STRING=str 'product photo of, clean white background, soft shadows, studio lighting, high...'; STRING=str 'clutter, dirty, blurry, watermark, text' |
| 15 | extra_negative = '' (empty) | PASS | STRING=str ''; STRING=str '' |

## Verdict

All 15 cases behaved as expected (15 passed, 0 rejected with a clear message).
