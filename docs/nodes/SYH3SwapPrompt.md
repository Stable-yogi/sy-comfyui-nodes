# H3 Swap Prompt SY (`SYH3SwapPrompt`)

Source: `nodes/sy_h3_swap_prompt.py`

**What it does:** Writes the instruction for swapping one person in a video for the character in a reference picture (a character swap with a reference-to-video model). It names who to replace, who to keep, and asks for the new face and body so the model does not change only the clothes.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| target | STRING | yes | Who to replace in the video. Name clothes or place: the man in the purple shirt, the girl on the left. | default 'the woman in the blue shirt' |
| take | COMBO | yes | What the new person takes from the reference picture. Face and hair keeps the clothes from the video. | one of: face and hair, face, hair and body, whole look |
| reference | STRING | yes | How the prompt names the reference picture or character sheet. | default 'Picture 1' |
| keep_expression | BOOLEAN | yes | On: ask to keep the facial expressions of the video too. | default True |
| keep | STRING | no | Other people or things that must not change, one per line or split by commas. Example: the boy. | default '', multiline |
| extra | STRING | no | One more sentence added at the end. | default '', multiline |

Outputs: `STRING`, `STRING`

## How to use

1. Give the MiniMax H3 Reference to Video node the picture of the new character (a character sheet works well) and the source video.
2. In target, say exactly who to swap with a short look, like "the man in the purple shirt". If other people are in the video, list them in keep.
3. Pick take: whole look takes face, hair, body and clothes; face and hair keeps the clothes from the video.
4. Connect prompt to the text input. Read notes: it warns about a vague target.
5. If only the clothes change, run 2 or 3 more seeds with the same prompt. Close, single people work best; many people, far away people and fast hair or body movement are harder.
