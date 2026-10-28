"""Helpers for the SY model loader nodes. Pure Python. comfy and folder_paths are imported only inside functions."""
import os

CLIP_TYPES = ["stable_diffusion", "stable_cascade", "sd3", "stable_audio", "mochi", "ltxv", "pixart", "cosmos",
              "lumina2", "wan", "hidream", "chroma", "ace", "omnigen2", "qwen_image", "hunyuan_image", "flux2",
              "ovis", "longcat_image", "cogvideox", "krea2", "flux3", "moss_image"]
CLIP_DEVICES = ["default", "cpu"]
UNET_DTYPES = ["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"]
# Folder choice for Loader Name Picker: friendly name -> ComfyUI folder key
MODEL_FOLDERS = {
    "checkpoints": "checkpoints",
    "loras": "loras",
    "vae": "vae",
    "clip": "text_encoders",
    "unet": "diffusion_models",
    "upscale_models": "upscale_models",
}


def format_size(num_bytes):
    """Pure function. 1536 -> '1.5 KB'. Uses 1024 steps."""
    n = float(num_bytes)
    if n < 0:
        raise ValueError("size cannot be negative, got %s" % num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d B" % n) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0


def info_line(name, num_bytes):
    """Pure function. One line with the file name and its size."""
    return "%s (%s)" % (name, format_size(num_bytes))


def check_choice(value, allowed, what):
    """Pure function. Value must be one of allowed, else a plain ValueError."""
    if value not in allowed:
        raise ValueError("%s %r is not one of: %s" % (what, value, ", ".join(allowed)))
    return value


def unet_options(weight_dtype):
    """Pure function. Weight dtype choice -> plain dict {'dtype': name or None, 'fp8_fast': bool}."""
    check_choice(weight_dtype, UNET_DTYPES, "weight_dtype")
    if weight_dtype == "default":
        return {"dtype": None, "fp8_fast": False}
    if weight_dtype == "fp8_e4m3fn_fast":
        return {"dtype": "float8_e4m3fn", "fp8_fast": True}
    return {"dtype": "float8_" + weight_dtype[4:], "fp8_fast": False}


def folder_key(folder):
    """Pure function. 'clip' -> 'text_encoders'. Refuses unknown folders."""
    check_choice(folder, list(MODEL_FOLDERS), "folder")
    return MODEL_FOLDERS[folder]


def pick_name(folder, name, names):
    """Pure function. Checks `name` is in the list of known files; returns it. Empty list gives a clear message."""
    folder_key(folder)
    if not names:
        raise ValueError("no files found in the %s folder. Put a model file there and refresh the list" % folder)
    if name not in names:
        raise ValueError("%r is not in the %s list. Refresh the list or pick another file" % (name, folder))
    return name


def listed_path(kind, name):
    """Full path of a file ComfyUI lists under `kind`. Raises ValueError for a name outside the list."""
    try:
        from ._sy_model_files import find_file
    except ImportError:
        from _sy_model_files import find_file
    return find_file(kind, name)


def embedding_dirs():
    import folder_paths
    return folder_paths.get_folder_paths("embeddings")
