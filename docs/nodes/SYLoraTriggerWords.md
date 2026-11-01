# LoRA Trigger Words SY (`SYLoraTriggerWords`)

Source: `nodes/sy_lora_trigger_words.py`

**What it does:** Reads the trigger words for a LoRA from a .json, .txt or .civitai.info file with the same name next to it. Can put them in front of your prompt (skipping words already there). An info line says where they came from, or what file to make.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| lora_name | COMBO | yes | The LoRA whose trigger words you want. | one of: None, test_lora.safetensors |
| separator | STRING | no | Text placed between the trigger words, for example a comma and a space. | default ', ' |
| prompt | STRING | no | Optional prompt. The prompt output is this text with the trigger words in front. | default '', multiline |

Outputs: `STRING`, `STRING`, `STRING`

## How to use

1. Pick the LoRA in lora_name. The node looks for a .json, .txt or .civitai.info file with the same name next to it.
2. Optional: change separator (default is a comma and a space) and type your own text in prompt.
3. Use the outputs: the trigger words, your prompt with the trigger words put in front (words already there are skipped), and an info line that says where the words came from or which file to create.
