# MOSS-Image workflows

ComfyUI workflows for the MOSS-Image picture model. They use the SY nodes in this pack and need ComfyUI 0.43 or newer (the MOSS-Image nodes are built in).

## SY - MOSS Image Speed Up v1

Text to picture with **MOSS Speed Up SY** between the model and **Sampler SY**. The speed-up node skips the full model on some steps and predicts them from the steps that ran. Pick a preset on the node: mild for signs and words, middle or strong for more speed, off for the normal picture. After a run the node shows how many steps it skipped.

Settings in the file: 1024 x 1024, 25 steps, er_sde sampler, simple scheduler, guidance 2.5, seed 42.

## Model files

| File | Folder |
|---|---|
| `moss_image_sft_int8_convrot.safetensors` | `models/diffusion_models` |
| `qwen3.5_9b_w4a8_gptq.safetensors` | `models/text_encoders` (loads with type moss_image) |
| `flux2-vae_small.safetensors` | `models/vae` |
