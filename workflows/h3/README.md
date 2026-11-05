# H3 workflows

Twelve ComfyUI workflows for the MiniMax H3 video model. They use the SY nodes in this pack.
Every workflow has a header box at the top: what it does, how to use it, and which model files it needs.
Groups marked **(optional)** are switched off at the start. Use the Group Switch SY panel next to the header to switch a group on.

## Model files

Eleven of the workflows carry a Model Downloader SY box at the top, next to the header. It lists the files below, shows which ones you already have, and downloads the missing ones from Hugging Face when you press a button (it shows the size and your free disk space and asks first). The two files that are not in the box: `RealESRGAN_x2.pth` and `minimax_h3_flf2v_lora_v1.safetensors` (get them by hand).

The same files are used by all twelve workflows. Put each file in the folder shown.

| File | Folder |
|---|---|
| `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | `models/diffusion_models` |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `models/text_encoders` |
| `minimax_h3_video_vae_int8_convrot.safetensors` | `models/vae` |
| `minimax_h3_audio_vae_fp32.safetensors` | `models/vae` |
| `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | `models/loras` (fast mode) |

Extra files for some workflows:

| File | Used by | Folder |
|---|---|---|
| `RealESRGAN_x2.pth` | Character Sheet (group 5), Upscale | `models/upscale_models` |
| `minimax_h3_flf2v_lora_v1.safetensors` | Turnaround (orbit group) | `models/loras` |
| `minimax_h3_fun_controlnet_union_2.0_pruned_int8_convrot.safetensors` | Video (exact layout group) | `models/model_patches` |

## The workflows

| File | What it makes |
|---|---|
| `SY - H3 Character Sheet v1.json` | One picture that shows your character from the front, the side and the back. |
| `SY - H3 Turnaround v1.json` | A short turn-around clip, plus a sheet of frames cut from it. |
| `SY - H3 Image v1.json` | One picture from up to four reference pictures. |
| `SY - H3 Image v2.json` | The same as Image v1, with fewer boxes: the model, reference pictures, prompt, sampler and saving each sit in one SY node. |
| `SY - H3 Voice v1.json` | A voice line from text, with an optional voice sample. |
| `SY - H3 Video v1.json` | A video with sound from a story, reference pictures, an optional acting clip, start and end pictures and a voice line. |
| `SY - H3 Upscale v1.json` | A sharper, bigger copy of a clip. The model draws fine detail again. |
| `SY - H3 Upscale RTX 4K v1.json` | A fast bigger copy of a clip with the RTX video upscaler. Needs an RTX graphics card and a ComfyUI that has the RTX Video Super Resolution node. |
| `SY - H3 Character Kit Free v1.json` | From one picture: a short look sheet video (12 shots), a labelled sheet of the best frame of each shot, and 3 reference pictures (face, full body, back). |
| `SY - H3 Talking Video Free v1.json` | One picture and a voice file (up to 15 seconds) become a talking or singing clip. The first frame is your picture and the lips follow your file. |
| `SY - H3 Recast Free v1.json` | Replace the person in a video (2 to 15 seconds) with your character. Same moves, same camera, same sound. Needs the character swap LoRA `h3_character_swap_v1.5.safetensors` in models/loras. If the old person stays for the first seconds, try 2 or 3 seeds. |
| `SY - H3 Story Studio Free v1.json` | Three shots made one after the other, each starting where the last one ended, joined into one video of about 21 seconds. |

## The one-frame trick

The model must make at least 5 frames. A frame count is always 5, 22, 39, 56 and so on (steps of 17, plus 5).
The picture workflows ask for exactly 5 frames and keep the first one. They finish in seconds and the character stays the same,
because the model sees your reference pictures while it draws.

## Fast mode

Each workflow has a switch called **Fast mode (turbo LoRA)**. On: 4 steps with the turbo file. Off: 20 steps and no turbo file.

The Video, Image, Character Sheet, Turnaround and Voice workflows also have a **Speed up** node (H3 Forecast Speed Up SY, preset mild). With fast mode off it skips the full model on 6 of the 20 steps, so a run takes about a quarter less time. With fast mode on it skips nothing. Set its preset to off for the exact normal result.

## Size

Width and height must be a multiple of 16. The Resolution node in these workflows snaps to 32.

## Notes

- The Upscale workflow draws every frame whole. A long or large clip needs a lot of video memory. Use a shorter clip or a smaller size if memory runs out.
- The characters, prompts and texts in these workflows are examples. Replace them with your own.
