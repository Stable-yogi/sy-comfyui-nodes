"""Helpers to list and find model files through ComfyUI's folder_paths. folder_paths is imported lazily."""
import os

NONE_NAME = "None"


def list_names(kind):
    """File names ComfyUI knows for `kind` ('checkpoints', 'loras', 'vae'). Empty list when comfy is not available."""
    try:
        import folder_paths
        return list(folder_paths.get_filename_list(kind))
    except Exception:
        return []


def check_relative(name):
    """Pure function. Refuses empty names, absolute paths and '..' parts."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("pick a file name")
    norm = name.replace("\\", "/")
    if norm.startswith("/") or (len(norm) > 1 and norm[1] == ":") or ".." in norm.split("/"):
        raise ValueError("file name must be a plain name from the list, not a path: %r" % name)
    return name


def find_file(kind, name):
    """Full path of a listed model file. Raises ValueError when the name is not in ComfyUI's list."""
    check_relative(name)
    try:
        import folder_paths
    except Exception:
        raise ValueError("ComfyUI folders are not available, so %r cannot be found" % name)
    if name not in folder_paths.get_filename_list(kind):
        raise ValueError("%r is not in the %s list. Refresh the list or pick another file." % (name, kind))
    path = folder_paths.get_full_path(kind, name)
    if not path or not os.path.isfile(path):
        raise ValueError("file for %r was not found on disk" % name)
    return path


def lora_stem(name):
    """Pure function. 'sub/my_lora.safetensors' -> 'my_lora'."""
    base = name.replace("\\", "/").split("/")[-1]
    stem, ext = os.path.splitext(base)
    return stem if ext.lower() in (".safetensors", ".ckpt", ".pt", ".pth", ".bin") else base


def fmt_strength(value):
    """Pure function. 0.8 -> '0.8', 1.0 -> '1'."""
    return ("%g" % round(float(value), 4))
