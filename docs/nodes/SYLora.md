# LoRA SY (`SYLora`)

Source: `nodes/sy_lora.py`

**What it does:** Applies one LoRA with an on/off switch (no bypassing), separate strengths for the picture model and the text encoder, and adds the LoRA's trigger words to your prompt for you. Chain several for a stack.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The model to add the LoRA to. |  |
| lora | COMBO | yes | The LoRA file. None = nothing is applied. | one of: None, test_lora.safetensors |
| enabled | BOOLEAN | yes | Off: everything passes through unchanged, no bypass needed. | default True |
| strength_model | FLOAT | yes | Strength on the picture model. | -20.0 to 20.0, step 0.05, default 1.0 |
| strength_clip | FLOAT | yes | Strength on the text encoder. Ignored when no clip is connected. | -20.0 to 20.0, step 0.05, default 1.0 |
| add_trigger_words | BOOLEAN | yes | On: reads the words from the .json or .txt file next to the LoRA and adds them to the prompt. | default True |
| position | COMBO | yes | Where the trigger words go. | one of: Before the prompt, After the prompt |
| clip | CLIP | no | The text encoder. Leave empty for models that need no clip LoRA. |  |
| prompt | STRING | no | Your prompt text. The trigger words are added to it. | default '' |

Outputs: `MODEL`, `CLIP`, `STRING`, `STRING`

## How to use

1. Connect your model to model. If your model uses a text encoder, connect clip too.
2. Pick the LoRA file in lora and set strength_model (picture) and strength_clip (text). Turn enabled off to pass everything through unchanged.
3. To get trigger words, keep add_trigger_words on, connect your prompt text to the prompt input (it is a socket, you cannot type in it), and choose Before the prompt or After the prompt in position. The words come from a .json or .txt file next to the LoRA.
4. Chain several LoRA SY nodes for a stack. Use the new model, clip and prompt from the outputs.
