# Power Lora Loader SY (`SYPowerLoraLoader`)

Source: `nodes/sy_power_lora.py`

**What it does:** Loads any number of LoRAs into the model and clip with one node. Each row has its own on/off switch, strength, optional separate clip strength and trigger words. The trigger_words output joins the words of every LoRA that was applied, without repeats, ready for your prompt. The master switch passes the model and clip on unchanged. Use the row editor on the node to add and pick LoRAs.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The model the LoRAs are applied to. |  |
| lora_rows | STRING | yes | The list of LoRAs. The row editor on the node fills this in; you do not type it. | default '[]' |
| all_on | BOOLEAN | yes | Master switch. Off passes the model and clip on unchanged. | default True |
| trigger_join | COMBO | yes | How the trigger words are joined in the trigger_words output. | one of: comma, newline, space |
| clip | CLIP | no | The text encoder. Without it only the model part of each LoRA is applied. |  |

Outputs: `MODEL`, `CLIP`, `STRING`, `STRING`

## How to use

1. Connect model, and clip if you have one. Without clip only the model part of each LoRA is applied.
2. Use the row editor on the node to add LoRAs. Each row has its own switch, strength, optional clip strength and trigger words. Do not type into lora_rows.
3. all_on is the master switch. Off passes model and clip on unchanged.
4. trigger_join sets how trigger_words are joined (comma, newline or space). The output holds the words of every applied LoRA, without repeats.
