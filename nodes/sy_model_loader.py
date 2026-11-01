"""Model Loader SY: one box that loads the model, the text encoder(s) and the VAE, with a Safetensors / GGUF switch."""
import os

try:
    from ._sy_common import category, register
    from ._sy_model_files import find_file, list_names
    from ._sy_loaders import UNET_DTYPES, unet_options, check_choice, format_size, embedding_dirs
    from . import _sy_gguf_names as N
    from .sy_gguf_loaders import _gguf_names, _clip_names, _clip_types, _runtime, _ensure_folders
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import find_file, list_names
    from _sy_loaders import UNET_DTYPES, unet_options, check_choice, format_size, embedding_dirs
    import _sy_gguf_names as N
    from sy_gguf_loaders import _gguf_names, _clip_names, _clip_types, _runtime, _ensure_folders

NONE = "(none)"
FORMATS = ["Safetensors", "GGUF"]


def is_none(name):
    """Pure function. True for an empty pick or the (none) entry."""
    return (not isinstance(name, str)) or name.strip() == "" or name == NONE


def with_none(names, first=False):
    """Pure function. The file list with the (none) entry added at the end (or at the start)."""
    names = [n for n in names if n != NONE]
    return ([NONE] + names) if first else (names + [NONE])


def plan_load(fmt, model_st, model_gg, enc_st, enc_gg, enc2, vae, audio_vae):
    """Pure function. Decides which files one pick of the switch loads. Raises a plain ValueError for a missing pick."""
    check_choice(fmt, FORMATS, "format")
    gguf = fmt == "GGUF"
    model = model_gg if gguf else model_st
    if is_none(model):
        if gguf:
            raise ValueError("Format is GGUF but no GGUF model is picked. Pick a file in model_gguf, or switch format to Safetensors.")
        raise ValueError("Format is Safetensors but no model is picked. Pick a file in model_safetensors, or switch format to GGUF.")
    if gguf and not N.is_gguf_name(model):
        raise ValueError("model_gguf must be a .gguf file, got %r" % model)
    enc1 = enc_gg if (gguf and not is_none(enc_gg)) else enc_st
    if is_none(enc1):
        raise ValueError("No text encoder is picked. Pick a file in text_encoder (or text_encoder_gguf).")
    encoders = [enc1]
    if not is_none(enc2):
        encoders.append(enc2)
    return {
        "format": fmt,
        "model": model,
        "encoders": encoders,
        "vae": None if is_none(vae) else vae,
        "audio_vae": None if is_none(audio_vae) else audio_vae,
    }


def info_text(plan, sizes=None):
    """Pure function. A short readable summary of what was loaded. sizes maps file name -> bytes (optional)."""
    sizes = sizes or {}

    def show(name):
        return "%s (%s)" % (name, format_size(sizes[name])) if name in sizes else str(name)

    lines = ["Format: %s" % plan["format"], "Model: %s" % show(plan["model"])]
    for i, enc in enumerate(plan["encoders"], start=1):
        lines.append("Text encoder %d: %s" % (i, show(enc)))
    lines.append("VAE: %s" % (show(plan["vae"]) if plan["vae"] else "none"))
    lines.append("Audio VAE: %s" % (show(plan["audio_vae"]) if plan["audio_vae"] else "none"))
    return "\n".join(lines)


def _plain_names(kind):
    return [n for n in list_names(kind) if not N.is_gguf_name(n)]


def _load_vae(path):
    import comfy.sd
    import comfy.utils
    sd, metadata = comfy.utils.load_torch_file(path, return_metadata=True)
    vae = comfy.sd.VAE(sd=sd, metadata=metadata)
    vae.throw_exception_if_invalid()
    return vae


class SYModelLoader:
    DESCRIPTION = ("Loads a whole model in one box: the diffusion model, the text encoder(s) and the VAE. "
                   "One switch changes the whole set between Safetensors and GGUF.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "VAE", "STRING")
    RETURN_NAMES = ("model", "clip", "vae", "audio_vae", "info")

    @classmethod
    def INPUT_TYPES(cls):
        enc_plain = _plain_names("text_encoders")
        enc_gguf = N.only_gguf(_clip_names())
        vaes = _plain_names("vae")
        return {
            "required": {
                "format": (FORMATS, {"default": "Safetensors", "tooltip": "The switch. Safetensors uses the normal files, GGUF uses the smaller GGUF files."}),
                "model_safetensors": (with_none(_plain_names("diffusion_models")), {"tooltip": "Diffusion model used when format is Safetensors."}),
                "model_gguf": (with_none(_gguf_names(N.UNET_KEY)), {"tooltip": "Diffusion model used when format is GGUF."}),
                "text_encoder": (with_none(enc_plain), {"tooltip": "Text encoder used with Safetensors (and with GGUF if no GGUF encoder is picked)."}),
                "text_encoder_gguf": (with_none(enc_gguf), {"tooltip": "Text encoder used when format is GGUF. Leave (none) to use the normal one."}),
                "family": (_clip_types(False), {"default": "stable_diffusion", "tooltip": "The model family the text encoder belongs to."}),
                "vae": (with_none(vaes), {"tooltip": "The VAE file. Pick (none) if you load the VAE somewhere else."}),
            },
            "optional": {
                "text_encoder_2": (with_none(enc_plain + enc_gguf, first=True), {"default": NONE, "tooltip": "A second text encoder, for models that use two. Leave (none) if not needed."}),
                "audio_vae": (with_none(vaes, first=True), {"default": NONE, "tooltip": "A second VAE for sound, used by video models with audio. Leave (none) otherwise."}),
                "weight_dtype": (UNET_DTYPES, {"default": "default", "tooltip": "Safetensors only. fp8 stores the model smaller. GGUF ignores this."}),
            },
        }

    def run(self, format, model_safetensors, model_gguf, text_encoder, text_encoder_gguf, family, vae,
            text_encoder_2=NONE, audio_vae=NONE, weight_dtype="default"):
        plan = plan_load(format, model_safetensors, model_gguf, text_encoder, text_encoder_gguf, text_encoder_2, vae, audio_vae)
        gguf = plan["format"] == "GGUF"
        check_choice(family, _clip_types(False), "family")
        _ensure_folders()
        model_path = find_file(N.UNET_KEY if gguf else "diffusion_models", plan["model"])
        enc_paths = [find_file(N.clip_folder_key(n), n) for n in plan["encoders"]]
        vae_path = find_file("vae", plan["vae"]) if plan["vae"] else None
        avae_path = find_file("vae", plan["audio_vae"]) if plan["audio_vae"] else None
        sizes = {}
        for name, path in [(plan["model"], model_path)] + list(zip(plan["encoders"], enc_paths)) + \
                [(plan["vae"], vae_path), (plan["audio_vae"], avae_path)]:
            if name and path:
                sizes[name] = os.path.getsize(path)

        if gguf:
            model = _runtime().load_unet(model_path)
        else:
            import torch
            import comfy.sd
            opts = unet_options(weight_dtype)
            model_options = {}
            if opts["dtype"]:
                model_options["dtype"] = getattr(torch, opts["dtype"])
            if opts["fp8_fast"]:
                model_options["fp8_optimizations"] = True
            model = comfy.sd.load_diffusion_model(model_path, model_options=model_options)

        if any(N.is_gguf_name(n) for n in plan["encoders"]):
            clip = _runtime().load_clip(enc_paths, family)
        else:
            import comfy.sd
            clip_type = getattr(comfy.sd.CLIPType, family.upper(), None)
            if clip_type is None:
                raise ValueError("this ComfyUI does not know the family %r. Pick another family" % family)
            clip = comfy.sd.load_clip(ckpt_paths=enc_paths, embedding_directory=embedding_dirs(), clip_type=clip_type, model_options={})

        vae_obj = _load_vae(vae_path) if vae_path else None
        avae_obj = _load_vae(avae_path) if avae_path else None
        return (model, clip, vae_obj, avae_obj, info_text(plan, sizes))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ModelLoader", SYModelLoader)
NODE_DISPLAY_NAME_MAPPINGS["SYModelLoader"] = "Model Loader SY"
