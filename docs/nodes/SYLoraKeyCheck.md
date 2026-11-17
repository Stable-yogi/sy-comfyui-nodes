# LoRA Key Check SY (`SYLoraKeyCheck`)

Source: `nodes/sy_lora_key_check.py`

**What it does:** Checks a LoRA against the loaded model before you use it. Says OK when every part fits, or lists the parts that do not fit (the 'lora key not loaded' lines in the console), so you can see if the LoRA is for another model. The model goes through unchanged.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The model the LoRA is meant for. It goes out unchanged. | |
| lora_name | COMBO | yes | The LoRA file to check. | one of: None, your LoRA files |
| clip | CLIP | no | Optional. Connect it if the LoRA also changes the text encoder, so those parts count as fitting. | |

Outputs: `MODEL` (model), `STRING` (report), `STRING` (unmatched_parts), `FLOAT` (match_percent)

## How to use

1. Put the node right after your model loader and pick the LoRA in lora_name. Connect clip as well if the LoRA was trained with the text encoder.
2. Run the workflow. The node shows a report: OK (every part fits), PARTLY (some parts fit) or NO MATCH (the LoRA is for another model).
3. unmatched_parts lists the parts that do not fit (up to 200), and match_percent gives the share that fits. The model output is the same model, so you can keep it in line.
