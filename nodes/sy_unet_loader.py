"""Unet Loader SY: loads a diffusion model file, with a choice of weight type."""
import os

try:
    from ._sy_common import category, register
    from ._sy_loaders import UNET_DTYPES, unet_options, listed_path
    from ._sy_model_files import list_names
    from ._sy_a2_files import read_header, kind_guess, main_dtype_text, gguf_refusal, size_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_loaders import UNET_DTYPES, unet_options, listed_path
    from _sy_model_files import list_names
    from _sy_a2_files import read_header, kind_guess, main_dtype_text, gguf_refusal, size_text

DTYPE_WORDS = {
    "default": "the type stored in the file",
    "fp8_e4m3fn": "8-bit floats (e4m3), about half the memory of fp16",
    "fp8_e4m3fn_fast": "8-bit floats (e4m3) with fast maths, about half the memory of fp16",
    "fp8_e5m2": "8-bit floats (e5m2), about half the memory of fp16, a little less exact",
}


def peek_header(path):
    """Reads the small safetensors header of the file, or None when it cannot be read (for example a GGUF file)."""
    if not str(path).lower().endswith(".safetensors"):
        return None
    try:
        return read_header(path)
    except (ValueError, OSError):
        return None


def check_is_diffusion_model(name, header):
    """Pure function. Refuses a file that is certainly a LoRA, with a plain sentence. Anything else passes."""
    if header is not None and kind_guess(header) == "LoRA":
        raise ValueError("%r is a LoRA, not a diffusion model. Load it with a LoRA loader and pick the base model here." % name)


def unet_info(name, weight_dtype, size_bytes=None, header=None, capability=None):
    """Pure function. A plain info text: file, size, what the file holds, how it is loaded, and notes."""
    first = name if size_bytes is None else "%s (%s)" % (name, size_text(size_bytes))
    lines = [first]
    notes = []
    if header is not None:
        lines.append("File holds: %s, %s" % (kind_guess(header), main_dtype_text(header)))
        kind = kind_guess(header)
        if kind not in ("diffusion model", "unknown"):
            notes.append("This file looks like a %s. If the model fails to work, pick a diffusion model file instead." % kind)
        if weight_dtype != "default" and "fp8" in main_dtype_text(header):
            notes.append("The file is already fp8, so the weight type does little. Use default.")
    elif str(name).lower().endswith(".gguf"):
        lines.append("File holds: GGUF (quantized)")
    lines.append("Loaded as: " + DTYPE_WORDS.get(weight_dtype, weight_dtype))
    if weight_dtype == "fp8_e4m3fn_fast" and capability is not None and tuple(capability) < (8, 9):
        notes.append("The fast fp8 type needs a graphics card of the RTX 40 series or newer. Use fp8_e4m3fn on this card.")
    return "\n".join(lines + notes)


class SYUnetLoader:
    DESCRIPTION = ("Loads a diffusion model (unet) file. The weight type can store it smaller in fp8 to save memory. "
                   "Checks the file first: a LoRA picked by mistake is refused in plain words, and the info output says what the file holds, "
                   "its size and how it was loaded.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "STRING")
    RETURN_NAMES = ("model", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "unet_name": (list_names("diffusion_models"), {"tooltip": "The diffusion model file to load."}),
                "weight_dtype": (UNET_DTYPES, {"default": "default", "tooltip": "default keeps the type stored in the file. fp8 uses less memory."}),
            }
        }

    def run(self, unet_name, weight_dtype):
        opts = unet_options(weight_dtype)
        refusal = gguf_refusal(unet_name, "Unet Loader SY", "Unet Loader GGUF SY")
        if refusal:
            raise ValueError(refusal)
        path = listed_path("diffusion_models", unet_name)
        header = peek_header(path)
        check_is_diffusion_model(unet_name, header)
        import torch
        import comfy.sd
        model_options = {}
        if opts["dtype"]:
            model_options["dtype"] = getattr(torch, opts["dtype"])
        if opts["fp8_fast"]:
            model_options["fp8_optimizations"] = True
        capability = torch.cuda.get_device_capability() if torch.cuda.is_available() else None
        info = unet_info(unet_name, weight_dtype, os.path.getsize(path), header, capability)
        return (comfy.sd.load_diffusion_model(path, model_options=model_options), info)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "UnetLoader", SYUnetLoader)
NODE_DISPLAY_NAME_MAPPINGS["SYUnetLoader"] = "Unet Loader SY"
