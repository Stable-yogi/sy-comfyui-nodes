# H3 Chain Settings SY (`SYH3ChainSettings`)

Source: `nodes/sy_h3_chain.py`

**What it does:** Everything the chain and the repair node both need: models, sampler, canvas and seed. Wire one of these into either.

session_name is read by H3 Render Segment (the first segment of a chain reads it, later ones inherit it from chain_state) but NOT by H3 Repair Segment, which has its own session_name.

chain_seed is deliberately not called 'seed': the ComfyUI page would add a randomise control to it and re-render the whole chain on every run.

ref_image_size: 'match' scales reference images to the video size. 'max' uses a 2048 pixel short edge for the best likeness and is several times slower.

handoff_mode: 'latent' (default) cuts the previous ending out of the previous segment's own latent and pins it. No VAE is used, so the anchor is exact and a VAE encode per segment is saved. 'pixel' decodes the ending, writes it as an mp4, reads it back and re-encodes it. It is slower and lossy, but it is the only way to change the picture size part way through a session. Both endings are always written to disk, so a session can be resumed in either mode. A session from before latent endings existed falls back to 'pixel' on its own.

drift_arrest: a long chain slowly drifts in colour and brightness because each segment only continues the last one. This pulls each handoff back toward segment 1 by the given fraction of the measured error (0 is off, 0.4 to 0.6 is the useful range). It is a fraction and not a reset, so no step shows at the joins, and large corrections are capped so a real lighting change is not fought. It needs handoff_mode 'latent'. Changing it re-renders the segments after the first. See docs/h3-chain.md.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| model | MODEL | yes | The H3 video model used for every segment. |  |
| clip | CLIP | yes | The text encoder that goes with the H3 model. |  |
| vae | VAE | yes | The H3 video VAE. |  |
| audio_vae | VAE | yes | The H3 audio VAE. |  |
| sampler | SAMPLER | yes | The sampler used for every segment. |  |
| sigmas | SIGMAS | yes | The noise steps (sigmas) used for every segment. |  |
| width | INT | yes | Picture width in pixels, in steps of 32. | 32 to 16384, step 32, default 864 |
| height | INT | yes | Picture height in pixels, in steps of 32. | 32 to 16384, step 32, default 480 |
| chain_seed | INT | yes | Each segment gets its own seed from this one. Changing it re-renders the whole chain. | 0 to 18446744073709551615, default 0 |
| session_name | STRING | yes | Folder name under output/h3_continuous/. The first segment of a chain reads it from here. | default 'my_chain' |
| ref_image_size | COMBO | yes | 'match' scales reference images to the video size. 'max' is sharper but several times slower. | one of: match, max |
| handoff_mode | COMBO | yes | 'latent' carries the ending over without a VAE (best). 'pixel' re-encodes it and can change size. | one of: latent, pixel |
| drift_arrest | FLOAT | yes | 0 is off. 0.4 to 0.6 pulls each handoff's colour back toward segment 1. Needs the latent handoff. | 0.0 to 1.0, step 0.05, default 0.0 |

Outputs: `SY_H3_SETTINGS`
