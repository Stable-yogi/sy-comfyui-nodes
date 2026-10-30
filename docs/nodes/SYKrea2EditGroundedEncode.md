# Krea2EditGroundedEncode SY (`SYKrea2EditGroundedEncode`)

Source: `nodes/sy_krea2_edit.py`

**What it does:** Encodes the edit instruction together with the source picture, so words like 'the man on the left' work.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| clip | CLIP | yes | The Krea 2 text encoder (Qwen3-VL with its vision part). |  |
| prompt | STRING | yes | The edit instruction. For the negative side, leave it empty and use the same image. | default '', multiline |
| image | IMAGE | no | The source picture the instruction refers to. Without it the node encodes text only. | picture batch [B,H,W,3] |
| image_b | IMAGE | no | Second reference (the subject) for two-reference edit LoRAs. Scene first, subject second. | picture batch [B,H,W,3] |
| grounding_px | INT | no | Longest side in pixels fed to the vision encoder. 0 keeps the native size. | 0 to 4096, step 64, default 768 |
| system_prompt | STRING | no | Advanced: replaces the built-in system prompt. Empty uses the training default. | default '', multiline |

Outputs: `CONDITIONING`
