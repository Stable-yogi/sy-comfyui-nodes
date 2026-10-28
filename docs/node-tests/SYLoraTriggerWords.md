# LoRA Trigger Words SY (`SYLoraTriggerWords`)

Source: `nodes/sy_lora_trigger_words.py`

**What it does:** Reads the trigger words for a LoRA from a .json or .txt file with the same name next to it. Empty when there is none.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| lora_name | COMBO | yes | The LoRA whose trigger words you want. | one of: None |

Outputs: `STRING`

## How it was tested

This node was not run by the harness. Reason: skipped: touches disk (the code reads or writes files).


## Verdict

Not run. skipped: touches disk (the code reads or writes files).
