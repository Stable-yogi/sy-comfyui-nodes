# H3SharpenHelper SY (`SYH3SharpenHelper`)

Source: `nodes/sy_h3_sharpen_helper.py`

**What it does:** Gets a Minimax H3 draft ready for the Open-H3 sharpen pass in one node: adds the Open-H3 LoRA and the shift (video 12, sound 3) to the model, makes the draft latent bigger with the H3 latent upscaler (the sound is kept), and gives the 3 tested steps. Connect model, latent and sigmas to a SamplerCustomAdvanced, and set an H3 Image To Video to the width and height it gives. Faces can change a little in this pass.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The H3 model from the draft (without the draft's own LoRAs is best). |  |
| draft_latent | LATENT | yes | The draft's joined video+sound latent, straight from the first sampler. |  |
| lora_name | COMBO | yes | The Open-H3 LoRA file from models/loras. | one of: test_lora.safetensors |
| lora_strength | FLOAT | yes | 1.0 is the tested value. | 0.0 to 2.0, step 0.05, default 1.0 |
| upscaler_name | COMBO | yes | The H3 latent upscaler file from models/latent_upscale_models. | one of: (none: put an H3 latent upscaler in models/latent_upscale_models) |
| scale | FLOAT | yes | How much bigger: 2.0 makes 1280 wide into 2560 wide. | 1.0 to 4.0, step 0.05, default 2.0 |
| fast_attention | BOOLEAN | yes | Use ComfyUI's faster attention for this pass when this ComfyUI has it. | default True |

Outputs: `MODEL`, `LATENT`, `SIGMAS`, `INT`, `INT`, `STRING`
