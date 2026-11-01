# H3 Guides SY (`SYH3Guides`)

Source: `nodes/sy_h3_guides.py`

**What it does:** Puts the optional guides for an H3 video into one box: a start picture, an end picture, a voice file and a layout video that the new clip follows. Leave a guide empty and it is skipped, so you never bypass nodes.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The video model. Only changed when a layout video is used. |  |
| positive | CONDITIONING | yes | The positive prompt conditioning to add the pins to. |  |
| latent | LATENT | yes | The empty video latent the pins are placed into. |  |
| layout_model | COMBO | yes | The layout (control) model file. Only needed with a layout video. | one of: None |
| layout_strength | FLOAT | yes | How strongly the clip follows the layout video. | 0.0 to 10.0, step 0.05, default 1.0 |
| vae | VAE | no | The video VAE. Needed for pictures and a layout video. |  |
| audio_vae | VAE | no | The audio VAE. Needed for a voice file. |  |
| start_image | IMAGE | no | Picture the clip starts with. | picture batch [B,H,W,3] |
| end_image | IMAGE | no | Picture the clip ends with. | picture batch [B,H,W,3] |
| voice | AUDIO | no | A voice file the clip follows, from the first frame. |  |
| layout_video | IMAGE | no | Frames of a depth, line or 3D layout video the new clip follows. | picture batch [B,H,W,3] |

Outputs: `MODEL`, `CONDITIONING`, `STRING`

## How to use

1. Connect model, positive, latent and the video vae. Connect audio_vae too if you use a voice file.
2. Connect any guides you want: start_image, end_image, voice, layout_video. A guide you leave empty is skipped, so no bypassing is needed.
3. With a layout video, pick layout_model and set layout_strength.
4. The model, the conditioning with the pins added, and an info line come out.
