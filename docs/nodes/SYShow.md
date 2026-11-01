# Show SY (`SYShow`)

Source: `nodes/sy_show.py`

**What it does:** One preview box for anything: shows text and numbers, previews pictures and video frames, and describes masks, latents and sound in plain words. The value passes through unchanged, so you can leave it in place.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| value | * | yes | Anything you want to look at. It also comes out unchanged on the output. |  |

Outputs: `*`

## How to use

1. Connect any output to value: text, number, picture, video frames, mask, latent or sound.
2. Text and numbers show in the node. Pictures preview. Masks, latents and sound are described in plain words.
3. The value passes through unchanged on the output, so the node can stay in the chain.
