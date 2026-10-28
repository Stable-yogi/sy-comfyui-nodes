"""Krea2 OneClick SY: the whole Krea 2 text-to-image pipeline in a single node.

Loads the model, text encoder and VAE, applies up to 3 LoRAs, samples, optionally runs a detail pass and
returns the image. ComfyUI pieces are imported only when the node runs.
"""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

# Tuned defaults for the Krea 2 family
QUALITY_PRESETS = {
    "Fast (8 steps)": {"steps": 8, "cfg": 1.0},
    "Best (16 steps)": {"steps": 16, "cfg": 2.0},
    "Max (20 steps)": {"steps": 20, "cfg": 3.0},
    "Custom": None,
}

SIZE_PRESETS = {
    "Portrait 2:3 (960x1440)": (960, 1440),
    "Portrait 2:3 big (1368x2048)": (1368, 2048),
    "Portrait 3:4 (1152x1536)": (1152, 1536),
    "Square 1:1 (1024x1024)": (1024, 1024),
    "Square 1:1 big (1536x1536)": (1536, 1536),
    "Landscape 3:2 (1440x960)": (1440, 960),
    "Landscape 3:2 big (2048x1368)": (2048, 1368),
    "Landscape 16:9 (1536x864)": (1536, 864),
    "Custom": None,
}

DETAIL_PASS = {"Off": 0.0, "Light": 0.25, "Full": 0.40}

# Hints are ordered best-first, so a loose word like "flux" never beats an exact one like "krea".
MODEL_HINTS = ("krea", "convrot", "muse", "flux")
CLIP_HINTS = ("qwen3vl_4b_fp8", "qwen3vl_4b", "qwen3vl", "qwen3-vl", "qwen3_vl")
VAE_HINTS = ("qwen_image_vae", "qwenimage", "qwen-image", "wan_2.1_vae", "wan2_1_vae", "wan2.1_vae")

AUTO = "auto"
NONE = "None"
FALLBACK_SAMPLERS = ["euler"]
FALLBACK_SCHEDULERS = ["simple"]


def rank_names(names, hints):
    """Pure function. Group names by which hint matched, best hint first; unmatched names last."""
    remaining = list(names)
    ranked = []
    for hint in hints:
        tier = [n for n in remaining if hint in n.lower()]
        ranked.extend(tier)
        remaining = [n for n in remaining if n not in tier]
    return ranked + remaining


def pick_auto(names, hints, what):
    """Pure function. First name matching the best hint. Raises ValueError telling the user to pick by hand."""
    for hint in hints:
        for n in names:
            if hint in n.lower():
                return n
    raise ValueError("could not auto-find a %s (looked for %s in: %s). Pick the %s in the dropdown by hand."
                     % (what, ", ".join(hints), ", ".join(names[:10]) if names else "an empty folder", what))


def quality_values(quality, custom_steps, custom_cfg):
    """Pure function. (steps, cfg) from the quality choice."""
    if quality not in QUALITY_PRESETS:
        raise ValueError("unknown quality %r; pick one of: %s" % (quality, ", ".join(QUALITY_PRESETS)))
    preset = QUALITY_PRESETS[quality]
    if preset is None:
        return custom_steps, custom_cfg
    return preset["steps"], preset["cfg"]


def size_values(size, custom_width, custom_height):
    """Pure function. (width, height) rounded down to a multiple of 8, at least 64."""
    if size not in SIZE_PRESETS:
        raise ValueError("unknown size %r; pick one of: %s" % (size, ", ".join(SIZE_PRESETS)))
    preset = SIZE_PRESETS[size]
    width, height = preset if preset else (custom_width, custom_height)
    return max(64, int(width) // 8 * 8), max(64, int(height) // 8 * 8)


def detail_denoise(detail_pass):
    """Pure function. Denoise strength of the optional second pass (0.0 = no pass)."""
    if detail_pass not in DETAIL_PASS:
        raise ValueError("unknown detail_pass %r; pick one of: %s" % (detail_pass, ", ".join(DETAIL_PASS)))
    return DETAIL_PASS[detail_pass]


def negative_mode(negative, cfg):
    """Pure function. How to build the negative: 'encode' (use the text), 'zero' (CFG 1 ignores it anyway)
    or 'empty' (encode an empty string; a zeroed one gives a black picture on GGUF files when CFG is above 1)."""
    if negative.strip():
        return "encode"
    return "zero" if cfg <= 1.0 else "empty"


def active_loras(requested):
    """Pure function. Keep only the LoRA slots that are set and not strength 0."""
    return [(name, s) for name, s in requested if name and name != NONE and s != 0.0]


def is_gguf(name):
    return name.lower().endswith(".gguf")


def _names(kind):
    try:
        import folder_paths
        return list(folder_paths.get_filename_list(kind))
    except Exception:
        return []


def _listing(kind, hints):
    names = _names(kind)
    return rank_names(names, hints) if names else ["(no %s found)" % kind]


def _gguf_names():
    """GGUF files, or nothing when the GGUF loader pack is not installed (it uses its own folder key)."""
    return _names("unet_gguf")


def _model_listing():
    names = _names("diffusion_models") + _gguf_names()
    return rank_names(names, MODEL_HINTS) if names else ["(no diffusion_models found)"]


def _samplers():
    try:
        import comfy.samplers
        return list(comfy.samplers.KSampler.SAMPLERS), list(comfy.samplers.KSampler.SCHEDULERS)
    except Exception:
        return list(FALLBACK_SAMPLERS), list(FALLBACK_SCHEDULERS)


def _load_diffusion_model(name, weight_dtype):
    import nodes
    if not is_gguf(name):
        return nodes.UNETLoader().load_unet(name, weight_dtype)[0]
    loader = nodes.NODE_CLASS_MAPPINGS.get("UnetLoaderGGUF")
    if loader is None:
        raise ValueError("%r is a GGUF file: install the GGUF loader pack or pick a safetensors model" % name)
    # GGUF carries its own quantisation, so weight_dtype does not apply.
    return getattr(loader(), loader.FUNCTION)(name)[0]


# A reference here keeps the weights loaded, so a seed change re-samples instead of re-reading the file.
_CACHE = {}


def _cached(kind, key, build):
    slot = _CACHE.get(kind)
    if slot is not None and slot[0] == key:
        return slot[1]
    value = build()
    _CACHE[kind] = (key, value)
    return value


def _apply_loras(unet, clip, requested):
    import nodes
    loader = nodes.LoraLoader()
    for name, strength in active_loras(requested):
        unet, clip = loader.load_lora(unet, clip, name, strength, strength)
    return unet, clip


class SYKrea2OneClick:
    DESCRIPTION = ("Krea 2 text-to-image in one node: loads the model, text encoder and VAE, applies up to 3 LoRAs, "
                   "samples, optionally runs a detail pass, and returns the image.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MODEL", "CLIP", "VAE", "CONDITIONING", "CONDITIONING", "LATENT")
    RETURN_NAMES = ("image", "model", "clip", "vae", "positive", "negative", "latent")

    @classmethod
    def INPUT_TYPES(cls):
        loras = [NONE] + _names("loras")
        samplers, schedulers = _samplers()
        return {
            "required": {
                "model": (_model_listing(), {"tooltip": "Krea 2 diffusion model. Safetensors works as is; GGUF needs the GGUF loader pack."}),
                "prompt": ("STRING", {"multiline": True, "default": "", "tooltip": "Describe the image to make. Empty text is allowed for testing."}),
                "negative": ("STRING", {"multiline": True, "default": "", "tooltip": "Describe what to avoid. Empty is handled safely at every CFG value."}),
                "quality": (list(QUALITY_PRESETS), {"default": "Best (16 steps)", "tooltip": "Sets steps and CFG together. Pick Custom to use custom_steps and custom_cfg."}),
                "size": (list(SIZE_PRESETS), {"default": "Portrait 2:3 (960x1440)", "tooltip": "Output size. Pick Custom to use custom_width and custom_height."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "control_after_generate": True, "tooltip": "Random seed. The same seed and settings give the same image."}),
                "detail_pass": (list(DETAIL_PASS), {"default": "Off", "tooltip": "Optional second pass: Light uses 0.25 denoise, Full uses 0.40."}),
            },
            "optional": {
                "lora_1": (loras, {"default": NONE, "tooltip": "First optional LoRA, applied to both the model and the text encoder."}),
                "lora_1_strength": ("FLOAT", {"default": 0.8, "min": -4.0, "max": 4.0, "step": 0.05, "tooltip": "Strength for LoRA 1. Set to 0 to skip this slot."}),
                "lora_2": (loras, {"default": NONE, "tooltip": "Second optional LoRA, applied after LoRA 1."}),
                "lora_2_strength": ("FLOAT", {"default": 0.8, "min": -4.0, "max": 4.0, "step": 0.05, "tooltip": "Strength for LoRA 2. Set to 0 to skip this slot."}),
                "lora_3": (loras, {"default": NONE, "tooltip": "Third optional LoRA, applied after LoRA 2."}),
                "lora_3_strength": ("FLOAT", {"default": 0.8, "min": -4.0, "max": 4.0, "step": 0.05, "tooltip": "Strength for LoRA 3. Set to 0 to skip this slot."}),
                "text_encoder": ([AUTO] + _listing("text_encoders", CLIP_HINTS), {"default": AUTO, "tooltip": "Qwen3-VL text encoder. Auto picks the best filename match; pick a file to override."}),
                "vae": ([AUTO] + _listing("vae", VAE_HINTS), {"default": AUTO, "tooltip": "Krea 2 compatible VAE. Auto prefers Qwen Image and falls back to Wan 2.1 names."}),
                "custom_steps": ("INT", {"default": 16, "min": 1, "max": 200, "tooltip": "Sampling steps, used only when quality is Custom."}),
                "custom_cfg": ("FLOAT", {"default": 2.0, "min": 0.0, "max": 20.0, "step": 0.1, "tooltip": "CFG, used only when quality is Custom."}),
                "custom_width": ("INT", {"default": 960, "min": 64, "max": 8192, "step": 16, "tooltip": "Width, used only for Custom size. Rounded down to a multiple of 8."}),
                "custom_height": ("INT", {"default": 1440, "min": 64, "max": 8192, "step": 16, "tooltip": "Height, used only for Custom size. Rounded down to a multiple of 8."}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 16, "tooltip": "Number of images made in one batch."}),
                "shift": ("FLOAT", {"default": 2.95, "min": 0.0, "max": 20.0, "step": 0.01, "tooltip": "Sampling shift. The measured Krea 2 default is 2.95."}),
                "sampler_name": (samplers, {"default": "euler", "tooltip": "Sampling algorithm. Euler is the measured default for Krea 2."}),
                "scheduler": (schedulers, {"default": "simple", "tooltip": "Noise schedule. Simple is the measured default for Krea 2."}),
                "weight_dtype": (["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"], {"default": "default", "tooltip": "Loader dtype for safetensors. Default respects the file; GGUF ignores it."}),
            },
        }

    def run(self, model, prompt, negative, quality, size, seed, detail_pass,
            lora_1=NONE, lora_1_strength=0.8, lora_2=NONE, lora_2_strength=0.8,
            lora_3=NONE, lora_3_strength=0.8, text_encoder=AUTO, vae=AUTO,
            custom_steps=16, custom_cfg=2.0, custom_width=960, custom_height=1440,
            batch_size=1, shift=2.95, sampler_name="euler", scheduler="simple",
            weight_dtype="default"):
        import torch
        import nodes

        steps, cfg = quality_values(quality, custom_steps, custom_cfg)
        width, height = size_values(size, custom_width, custom_height)
        boost = detail_denoise(detail_pass)

        clip_name = text_encoder
        if clip_name == AUTO:
            clip_name = pick_auto(_names("text_encoders"), CLIP_HINTS, "text encoder")
        vae_name = vae
        if vae_name == AUTO:
            vae_name = pick_auto(_names("vae"), VAE_HINTS, "VAE")

        unet = _cached("unet", (model, weight_dtype), lambda: _load_diffusion_model(model, weight_dtype))
        clip = _cached("clip", clip_name, lambda: nodes.CLIPLoader().load_clip(clip_name, "krea2", "default")[0])
        vae_obj = _cached("vae", vae_name, lambda: nodes.VAELoader().load_vae(vae_name)[0])

        unet, clip = _apply_loras(unet, clip, [(lora_1, lora_1_strength), (lora_2, lora_2_strength), (lora_3, lora_3_strength)])

        aura = nodes.NODE_CLASS_MAPPINGS.get("ModelSamplingAuraFlow")
        if aura is None:
            raise ValueError("this ComfyUI has no ModelSamplingAuraFlow node; update ComfyUI")
        unet = aura().patch_aura(unet, shift)[0]

        encoder = nodes.CLIPTextEncode()
        positive = encoder.encode(clip, prompt)[0]
        mode = negative_mode(negative, cfg)
        if mode == "encode":
            negative_cond = encoder.encode(clip, negative)[0]
        elif mode == "zero":
            negative_cond = nodes.ConditioningZeroOut().zero_out(positive)[0]
        else:
            negative_cond = encoder.encode(clip, "")[0]

        latent = {"samples": torch.zeros([batch_size, 16, height // 8, width // 8])}
        sampled = nodes.common_ksampler(unet, seed, steps, cfg, sampler_name, scheduler,
                                        positive, negative_cond, latent, denoise=1.0)[0]
        if boost > 0.0:
            sampled = nodes.common_ksampler(unet, seed + 1, steps, cfg, sampler_name, scheduler,
                                            positive, negative_cond, sampled, denoise=boost)[0]

        image = nodes.VAEDecode().decode(vae_obj, sampled)[0]
        # The model is returned after LoRAs and shift so a later detail or face pass uses the same weights.
        return (image, unet, clip, vae_obj, positive, negative_cond, sampled)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Krea2OneClick", SYKrea2OneClick)
