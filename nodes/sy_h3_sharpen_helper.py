"""H3 Sharpen Helper SY: gets a Minimax H3 draft ready for the Open-H3 sharpen pass in one node.
It adds the Open-H3 LoRA and the shift to the model, makes the draft video latent bigger (sound kept), and gives the
3 tested steps. Feed its outputs to a sampler (SamplerCustomAdvanced) with an H3 Image To Video at the new size."""
try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names

# The only step list tested with the Open-H3 LoRA (3 Euler steps). Other step counts are not known to work.
SHARPEN_SIGMAS = (0.909375, 0.857143, 0.666667, 0.0)
NO_LORA = "(none: put the Open-H3 LoRA in models/loras)"
NO_UPSCALER = "(none: put an H3 latent upscaler in models/latent_upscale_models)"
FACE_NOTE = ("The sharpen pass draws the picture again, so faces can change a little. "
             "When a face must stay exactly the same, use a plain upscaler (for example SeedVR2) instead.")


def pick_default(names, words):
    """Pure function. First name (by order of `words`) that holds one of the words, else the first name."""
    low = [(n, n.lower()) for n in names]
    for w in words:
        for n, l in low:
            if w in l:
                return n
    return names[0] if names else ""


def sigma_text(sigmas=SHARPEN_SIGMAS):
    """Pure function. The steps as the text a Manual Sigmas node takes."""
    return ", ".join(("%.6f" % s).rstrip("0").rstrip(".") if s else "0.0" for s in sigmas)


def check_inputs(lora_name, upscaler_name, scale, lora_strength):
    """Pure function. Raises ValueError with a plain fix when an input cannot work. Returns a list of warnings."""
    if not lora_name or lora_name == NO_LORA:
        raise ValueError("no LoRA picked: put the Open-H3 LoRA file in ComfyUI/models/loras and refresh (press R)")
    if not upscaler_name or upscaler_name == NO_UPSCALER:
        raise ValueError("no latent upscaler picked: put the H3 latent upscaler file in ComfyUI/models/latent_upscale_models and refresh")
    if not 1.0 <= float(scale) <= 4.0:
        raise ValueError("scale must be between 1 and 4, got %s" % scale)
    warn = []
    if "open" not in lora_name.lower():
        warn.append("The picked LoRA name does not say 'open'. The 3 steps were tested with the Open-H3 LoRA only.")
    if abs(float(lora_strength) - 1.0) > 1e-6:
        warn.append("LoRA strength is %.2f. The tested value is 1.0." % float(lora_strength))
    return warn


def build_notes(w_px, h_px, frames, warnings):
    lines = ["H3 SHARPEN HELPER", "New size: %d x %d pixels, %d latent frames." % (w_px, h_px, frames),
             "Set the H3 Image To Video node after this one to %d x %d." % (w_px, h_px),
             "Steps: %s (Euler sampler)." % sigma_text(), FACE_NOTE]
    lines += ["NOTE " + w for w in warnings]
    return "\n".join(lines)


class SYH3SharpenHelper:
    DESCRIPTION = ("Gets a Minimax H3 draft ready for the Open-H3 sharpen pass in one node: adds the Open-H3 LoRA and the "
                   "shift (video 12, sound 3) to the model, makes the draft latent bigger with the H3 latent upscaler "
                   "(the sound is kept), and gives the 3 tested steps. Connect model, latent and sigmas to a "
                   "SamplerCustomAdvanced, and set an H3 Image To Video to the width and height it gives. "
                   "Faces can change a little in this pass.")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "LATENT", "SIGMAS", "INT", "INT", "STRING")
    RETURN_NAMES = ("model", "latent", "sigmas", "width", "height", "notes")

    @classmethod
    def INPUT_TYPES(cls):
        loras = list_names("loras") or [NO_LORA]
        ups = list_names("latent_upscale_models") or [NO_UPSCALER]
        return {"required": {
            "model": ("MODEL", {"tooltip": "The H3 model from the draft (without the draft's own LoRAs is best)."}),
            "draft_latent": ("LATENT", {"tooltip": "The draft's joined video+sound latent, straight from the first sampler."}),
            "lora_name": (loras, {"default": pick_default(loras, ("open_regenerate", "open-h3", "openh3", "open")),
                                  "tooltip": "The Open-H3 LoRA file from models/loras."}),
            "lora_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05, "tooltip": "1.0 is the tested value."}),
            "upscaler_name": (ups, {"default": pick_default(ups, ("minimax_h3", "h3")),
                                    "tooltip": "The H3 latent upscaler file from models/latent_upscale_models."}),
            "scale": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 4.0, "step": 0.05, "tooltip": "How much bigger: 2.0 makes 1280 wide into 2560 wide."}),
            "fast_attention": ("BOOLEAN", {"default": True, "tooltip": "Use ComfyUI's faster attention for this pass when this ComfyUI has it."}),
        }}

    def run(self, model, draft_latent, lora_name, lora_strength, upscaler_name, scale, fast_attention=True):
        import torch
        try:
            from ._sy_core_call import core
            from .sy_h3_latent_upscaler import SYH3LatentUpscaler, VAE_DOWNSAMPLE
        except ImportError:
            from _sy_core_call import core
            from sy_h3_latent_upscaler import SYH3LatentUpscaler, VAE_DOWNSAMPLE
        warnings = check_inputs(lora_name, upscaler_name, scale, lora_strength)
        who = "H3 Sharpen Helper SY"
        m = core("LoraLoaderModelOnly", who, model=model, lora_name=lora_name, strength_model=float(lora_strength))[0]
        m = core("MiniMaxH3SigmaShift", who, model=m, shift_video=12, shift_audio=3)[0]
        if fast_attention:
            try:
                m = core("ModelAttentionBackend", who, model=m, attention="comfy kitchen attention")[0]
            except Exception as e:  # older ComfyUI: the pass still works, only slower
                warnings.append("Fast attention is not in this ComfyUI (%s); the pass runs at normal speed." % str(e).split("\n")[0][:120])
        video, audio = core("LTXVSeparateAVLatent", who, av_latent=draft_latent)[:2]
        big = SYH3LatentUpscaler().run(video, upscaler_name, "scale by multiplier", float(scale), 1280, 704, 1.0, 32,
                                       True, True, "cuda", "bf16")[0]
        joined = core("LTXVConcatAVLatent", who, video_latent=big, audio_latent=audio)[0]
        s = big["samples"]
        w_px, h_px, frames = int(s.shape[-1]) * VAE_DOWNSAMPLE, int(s.shape[-2]) * VAE_DOWNSAMPLE, int(s.shape[2]) if s.dim() == 5 else 1
        sigmas = torch.tensor(SHARPEN_SIGMAS, dtype=torch.float32)
        return (m, joined, sigmas, w_px, h_px, build_notes(w_px, h_px, frames, warnings))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3SharpenHelper", SYH3SharpenHelper)
