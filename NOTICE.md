# Notice
The code is MIT (see LICENSE). The name "Stable Yogi", "SY", the logo and the head picture are NOT covered by the MIT licence.
Fonts, if any are bundled, are listed here with their own licence. None are bundled yet.
This is an independent community extension. It is not affiliated with Comfy Org or the ComfyUI project.

## Third-party code
Some nodes are ported from open-source packs. Each was renamed and adapted to the SY standard. The original licence text sits in `third_party/<pack>/LICENSE`.

| Pack | Author | Licence | Where it went |
|---|---|---|---|
| comfyui-krea2edit | lbouaraba (repository owner) | Apache-2.0 | ported into SY nodes: `nodes/sy_krea2_edit.py` (Krea2EditModelPatch, Krea2EditGroundedEncode) |
| comfyui-krea2-conditioning | Hu White | Apache-2.0 | ported into SY nodes: `nodes/sy_krea2_conditioning.py` (Krea2ConditioningRebalance) |
| ComfyUI-Krea2T-Enhancer | capitan01R | MIT | ported into SY nodes: `nodes/sy_krea2t_enhancer.py` (Krea2TEnhancer, Krea2TEnhancerAdvanced) |
| ComfyUI Minimax H3 Latent Upscaler | LBH-123-AI | MIT | ported into an SY node: `nodes/sy_h3_latent_upscaler.py` (the 3D upscaler). The trained model file (Apache-2.0, same author) is not bundled; users download it themselves |
| ComfyUI-GGUF | city96 | Apache-2.0 | ported into SY nodes: `nodes/sy_gguf_loaders.py` and helpers `nodes/_sy_gguf_*.py` (Unet, CLIP and Dual CLIP GGUF loaders). Needs the `gguf` pip package at run time |
| ComfyUI-TeaCache | Copyright 2024 TeaCache | Apache-2.0 | ported into SY nodes: `nodes/sy_h3_speed.py` and helpers `nodes/_sy_h3_*.py` (H3 speed optimizer and low-VRAM helper). The optional sparse kernel is not bundled |
