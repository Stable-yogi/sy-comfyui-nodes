"""VAE Loader SY: loads one VAE file from the vae folder."""
import os

try:
    from ._sy_common import category, register
    from ._sy_loaders import listed_path
    from ._sy_model_files import list_names
    from ._sy_a2_files import read_header, kind_guess, main_dtype_text, gguf_refusal, size_text
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_loaders import listed_path
    from _sy_model_files import list_names
    from _sy_a2_files import read_header, kind_guess, main_dtype_text, gguf_refusal, size_text

# words in a VAE file name that name a model family (a hint only; a name can be wrong)
FAMILY_WORDS = (("flux", "Flux"), ("sdxl", "SDXL"), ("sd3", "SD3"), ("sd15", "SD 1.5"), ("sd1", "SD 1.5"), ("wan", "Wan"),
                ("qwen", "Qwen Image"), ("hunyuan", "Hunyuan"), ("ltx", "LTX"), ("krea", "Krea"), ("moss", "MOSS"))
NOT_A_VAE = ("LoRA", "diffusion model", "text encoder", "full checkpoint (model + VAE/text encoder)")
BIG_VAE_BYTES = 2 * 1024 ** 3


def peek_header(path):
    """The small safetensors header of the file, or None when it cannot be read."""
    if not str(path).lower().endswith(".safetensors"):
        return None
    try:
        return read_header(path)
    except (ValueError, OSError):
        return None


def check_is_vae(name, header):
    """Pure function. Refuses a file that is clearly not a VAE (a LoRA, a model, a text encoder), with a plain sentence."""
    if header is None:
        return
    kind = kind_guess(header)
    if kind in NOT_A_VAE:
        raise ValueError("%r looks like a %s, not a VAE. Pick a file from the vae list that is meant to be a VAE." % (name, kind.split(" (")[0]))


def family_hint(name):
    """Pure function. The model family a VAE file name points to, or ''."""
    low = os.path.basename(str(name).replace(chr(92), "/")).lower()
    for word, family in FAMILY_WORDS:
        if word in low:
            return family
    return ""


def vae_info(name, size_bytes=None, header=None):
    """Pure function. A plain info text: file, size, data type, and a family hint."""
    lines = [name if size_bytes is None else "%s (%s)" % (name, size_text(size_bytes))]
    if header is not None:
        lines.append("File holds: %s" % main_dtype_text(header))
    fam = family_hint(name)
    if fam:
        lines.append("The name points to %s. Use this VAE only with a %s model." % (fam, fam))
    else:
        lines.append("The name does not say which model family it fits. A VAE must match the model: SD 1.5, SDXL, Flux and Wan VAEs are not interchangeable.")
    if size_bytes is not None and size_bytes > BIG_VAE_BYTES:
        lines.append("This file is unusually big for a VAE (%s)." % size_text(size_bytes))
    return chr(10).join(lines)


class SYVAELoader:
    DESCRIPTION = ("Loads a single VAE file from your vae folder. Refuses a LoRA, a model or a text encoder picked by mistake, "
                   "and the info output gives the file size, data type and which model family the name points to.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("VAE", "STRING")
    RETURN_NAMES = ("vae", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vae_name": (list_names("vae"), {"tooltip": "The VAE file to load from the vae folder."}),
            }
        }

    def run(self, vae_name):
        refusal = gguf_refusal(vae_name, "VAE Loader SY")
        if refusal:
            raise ValueError(refusal)
        path = listed_path("vae", vae_name)
        header = peek_header(path)
        check_is_vae(vae_name, header)
        import comfy.sd
        import comfy.utils
        sd, metadata = comfy.utils.load_torch_file(path, return_metadata=True)
        vae = comfy.sd.VAE(sd=sd, metadata=metadata)
        vae.throw_exception_if_invalid()
        return (vae, vae_info(vae_name, os.path.getsize(path), header))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VAELoader", SYVAELoader)
NODE_DISPLAY_NAME_MAPPINGS["SYVAELoader"] = "VAE Loader SY"
