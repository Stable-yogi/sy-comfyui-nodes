# Model Preset Bundle SY (`SYModelPresetBundle`)

Source: `nodes/sy_model_preset_bundle.py`

**What it does:** Pick a model family and get its usual steps, cfg, sampler, scheduler, size and a short note. These are starting points.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| preset | COMBO | yes | The model family whose usual settings you want. | one of: Krea 2, Qwen Image 2.1, Flux, SDXL (old), Z-Image, Wan 2.2 video, LTX video, H3, MiniMax image, MiniMax video, HunyuanVideo, Qwen edit ... |

Outputs: `INT`, `FLOAT`, `STRING`, `STRING`, `INT`, `INT`, `STRING`

## How it was tested

The harness builds a starting set of inputs from the default of every input (first entry for lists, a small gradient picture for IMAGE and a mask with a filled box for MASK). It runs the node once like that, then changes one input at a time: every entry of every list, the lowest, highest and a middle value of every number, both settings of every on/off switch, and an empty text for every text box. Each run must give the right number of outputs, and pictures and masks must have sane dimensions and no broken (NaN) values. A plain-words refusal to an out-of-range number or empty text counts as REJECTED (expected). Any other error counts as FAIL. The node was run in a temporary folder.

## Cases

| # | Input changed | Result | Output / message |
|---|---|---|---|
| 1 | baseline (all defaults) | PASS | INT=int 28; FLOAT=float 3.5; STRING=str 'euler'; STRING=str 'simple'; INT=int 1024; INT=int 1024; STRING=str 'Starting point for Krea 2 pictures. Raise steps for fine detail.' |
| 2 | preset = 'Qwen Image 2.1' | PASS | INT=int 30; FLOAT=float 4; STRING=str 'euler'; STRING=str 'simple'; INT=int 1328; INT=int 1328; STRING=str 'Starting point for Qwen Image 2.1. Good with long, plain-sentence prompts.' |
| 3 | preset = 'Flux' | PASS | INT=int 20; FLOAT=float 1; STRING=str 'euler'; STRING=str 'simple'; INT=int 1024; INT=int 1024; STRING=str 'Flux uses its own built-in guidance, so cfg stays at 1.' |
| 4 | preset = 'SDXL (old)' | PASS | INT=int 30; FLOAT=float 7; STRING=str 'dpmpp_2m'; STRING=str 'karras'; INT=int 1024; INT=int 1024; STRING=str 'Classic SDXL settings. Keep sizes near one megapixel.' |
| 5 | preset = 'Z-Image' | PASS | INT=int 8; FLOAT=float 1; STRING=str 'res_multistep'; STRING=str 'simple'; INT=int 1024; INT=int 1024; STRING=str 'Z-Image turbo style: few steps, cfg 1.' |
| 6 | preset = 'Wan 2.2 video' | PASS | INT=int 20; FLOAT=float 3.5; STRING=str 'uni_pc'; STRING=str 'simple'; INT=int 832; INT=int 480; STRING=str 'Wan 2.2 video starting point. Frame count is set elsewhere.' |
| 7 | preset = 'LTX video' | PASS | INT=int 30; FLOAT=float 3; STRING=str 'euler'; STRING=str 'simple'; INT=int 768; INT=int 512; STRING=str 'LTX video starting point. Multiples of 32 work best for size.' |
| 8 | preset = 'H3' | PASS | INT=int 25; FLOAT=float 4; STRING=str 'euler'; STRING=str 'simple'; INT=int 1024; INT=int 1024; STRING=str 'General starting point for H3. Adjust after a first test.' |
| 9 | preset = 'MiniMax image' | PASS | INT=int 30; FLOAT=float 4; STRING=str 'euler'; STRING=str 'normal'; INT=int 1024; INT=int 1024; STRING=str 'General starting point for MiniMax pictures.' |
| 10 | preset = 'MiniMax video' | PASS | INT=int 30; FLOAT=float 5; STRING=str 'euler'; STRING=str 'normal'; INT=int 1280; INT=int 720; STRING=str 'General starting point for MiniMax video, 16:9.' |
| 11 | preset = 'HunyuanVideo' | PASS | INT=int 30; FLOAT=float 1; STRING=str 'euler'; STRING=str 'simple'; INT=int 848; INT=int 480; STRING=str 'HunyuanVideo uses embedded guidance, so cfg stays at 1.' |
| 12 | preset = 'Qwen edit' | PASS | INT=int 20; FLOAT=float 4; STRING=str 'euler'; STRING=str 'simple'; INT=int 1024; INT=int 1024; STRING=str 'Starting point for Qwen picture editing.' |
| 13 | preset = 'SD 1.5' | PASS | INT=int 25; FLOAT=float 7; STRING=str 'dpmpp_2m'; STRING=str 'karras'; INT=int 512; INT=int 512; STRING=str 'Classic SD 1.5 settings. Stay near 512 pixels, then upscale.' |
| 14 | preset = 'Generic' | PASS | INT=int 20; FLOAT=float 5; STRING=str 'euler'; STRING=str 'normal'; INT=int 1024; INT=int 1024; STRING=str 'Neutral starting point for any model.' |

## Verdict

All 14 cases behaved as expected (14 passed, 0 rejected with a clear message).
