# LTX Latent Bridge SY (`SYLtxLatentBridge`)

Source: `nodes/sy_ltx_latent_bridge.py`

**What it does:** Turns decoded video frames (for example from an H3 decode) into an LTX-shaped latent in one node. It fits the size to a multiple of 32, fits the frame count to 8n+1, and encodes with the LTX VAE you connect. The info line says what changed. Also gives the fitted frames, so you can preview them.

## Inputs

| Input | Type | Required | What it does | Range / options |
|---|---|---|---|---|
| images | IMAGE | yes | The decoded frames, for example the picture output of an H3 VAE Decode. | picture batch [B,H,W,3] |
| vae | VAE | yes | The LTX VAE used to encode the frames. |  |
| frame_policy | COMBO | yes | When the count is not 8n+1: exact stops with an error, trim cuts, pad repeats the last frame, nearest picks the closest. | one of: exact, trim, pad, nearest |
| resize_mode | COMBO | yes | stretch fills the new size (tiny shape change). crop keeps the shape and trims the edges. | one of: stretch, crop |
| max_pixels | FLOAT | no | Pixel budget in megapixels. 0 is off: the size is only rounded to the multiple. | 0.0 to 1000.0, step 0.01, default 0.0 |
| multiple_of | INT | no | Width and height are made a multiple of this number. LTX wants 32. | 1 to 256, default 32 |
| frame_step | INT | no | The n in the frame rule step*n+1. LTX wants 8. | 1 to 64, default 8 |

Outputs: `LATENT`, `IMAGE`, `INT`, `INT`, `INT`, `STRING`

## How to use

1. Decode the H3 result to pictures with your H3 VAE Decode.
2. Connect those pictures to **images** and your LTX VAE to **vae**.
3. Leave **frame_policy** on trim (cuts the few extra frames from the end) or pick pad to repeat the last frame instead. Use exact if you want an error rather than a change.
4. Connect **latent** to the LTX part of your workflow. The **info** line tells what changed, and **images** shows the frames that were really encoded.
5. For a smaller, faster clip set **max_pixels** (for example 0.5). The size stays a multiple of 32.
