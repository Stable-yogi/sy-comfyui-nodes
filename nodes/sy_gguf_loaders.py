"""GGUF loaders SY: load a GGUF diffusion model or text encoder (one or two files). LoRA keeps working.

Ported from ComfyUI-GGUF (Apache-2.0, city96). Changed for the SY pack by Stable Yogi.
Original copyright: (c) City96. Licence copy: third_party/ComfyUI-GGUF/LICENSE.

Nodes: UnetLoaderGGUF, CLIPLoaderGGUF, DualCLIPLoaderGGUF. The heavy code lives in nodes/_sy_gguf_runtime.py
and nodes/_sy_gguf_dequant.py. They need torch and the Python package gguf, and are loaded only when a
GGUF file is really opened, so this file imports cleanly on any computer.
"""
try:
    from ._sy_common import category, register
    from ._sy_model_files import find_file
    from . import _sy_gguf_names as N
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import find_file
    import _sy_gguf_names as N


def _ensure_folders():
    """Register the two GGUF file lists with ComfyUI (same folders as the normal loaders, .gguf only). Safe to repeat."""
    import folder_paths
    known = folder_paths.folder_names_and_paths
    for key, bases in ((N.UNET_KEY, N.UNET_BASE_KEYS), (N.CLIP_KEY, N.CLIP_BASE_KEYS)):
        if key in known:
            continue
        target = next((b for b in bases if b in known), bases[0])
        folders, _ext = known.get(target, ([], set()))
        known[key] = (folders, {N.GGUF_EXT})


def _gguf_names(key):
    try:
        import folder_paths
        _ensure_folders()
        return N.only_gguf(folder_paths.get_filename_list(key))
    except Exception:
        return []  # ComfyUI folders not available (selftest): the list is simply empty


def _clip_names():
    try:
        import folder_paths
        _ensure_folders()
        return N.clip_choices(folder_paths.get_filename_list(N.CLIP_BASE_KEYS[0]),
                              folder_paths.get_filename_list(N.CLIP_KEY))
    except Exception:
        return []


def _clip_types(dual):
    """The clip type list of THIS ComfyUI, so new model families work without an update here."""
    try:
        import nodes
        loader = nodes.DualCLIPLoader if dual else nodes.CLIPLoader
        live = list(loader.INPUT_TYPES()["required"]["type"][0])
        if live:
            return live
    except Exception:
        pass  # ComfyUI not loaded (selftest): use the fixed list
    return list(N.CLIP_TYPES_FALLBACK)


def _runtime():
    """Load the heavy helper. Gives a plain message when the gguf package is missing."""
    try:
        import gguf  # noqa: F401
    except ImportError:
        raise ValueError(N.INSTALL_MESSAGE)
    try:
        from . import _sy_gguf_runtime as rt
    except ImportError:
        import _sy_gguf_runtime as rt
    return rt


def _clip_path(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("pick a text encoder file")
    _ensure_folders()
    return find_file(N.clip_folder_key(name), name)


class SYUnetLoaderGGUF:
    DESCRIPTION = "Loads a GGUF diffusion model (unet). Smaller than the full file and LoRA files still work on it. Needs the gguf Python package (the node tells you how to add it)."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("model",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "unet_name": (_gguf_names(N.UNET_KEY), {"tooltip": "The .gguf diffusion model file to load."}),
            }
        }

    def run(self, unet_name):
        N.check_unet_name(unet_name)
        _ensure_folders()
        path = find_file(N.UNET_KEY, unet_name)
        rt = _runtime()
        return (rt.load_unet(path),)


class SYCLIPLoaderGGUF:
    DESCRIPTION = "Loads one text encoder (CLIP) file. It can be a .gguf file or a normal one. Pick the model family. A .gguf file needs the gguf Python package (the node tells you how to add it)."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("CLIP",)
    RETURN_NAMES = ("clip",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip_name": (_clip_names(), {"tooltip": "The text encoder file to load (.gguf or normal)."}),
                "type": (_clip_types(False), {"default": "stable_diffusion", "tooltip": "The model family this text encoder is used with."}),
            }
        }

    def run(self, clip_name, type="stable_diffusion"):
        N.check_clip_type(type, _clip_types(False))
        path = _clip_path(clip_name)
        rt = _runtime()
        return (rt.load_clip([path], type),)


class SYDualCLIPLoaderGGUF:
    DESCRIPTION = "Loads two text encoder files together. Each can be a .gguf file or a normal one. Pick the model family. A .gguf file needs the gguf Python package (the node tells you how to add it)."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("CLIP",)
    RETURN_NAMES = ("clip",)

    @classmethod
    def INPUT_TYPES(cls):
        names = _clip_names()
        return {
            "required": {
                "clip_name1": (names, {"tooltip": "The first text encoder file (.gguf or normal)."}),
                "clip_name2": (names, {"tooltip": "The second text encoder file (.gguf or normal)."}),
                "type": (_clip_types(True), {"default": "stable_diffusion", "tooltip": "The model family these two encoders are used with."}),
            }
        }

    def run(self, clip_name1, clip_name2, type="stable_diffusion"):
        N.check_clip_type(type, _clip_types(True))
        paths = [_clip_path(clip_name1), _clip_path(clip_name2)]
        rt = _runtime()
        return (rt.load_clip(paths, type),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "UnetLoaderGGUF", SYUnetLoaderGGUF)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CLIPLoaderGGUF", SYCLIPLoaderGGUF)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DualCLIPLoaderGGUF", SYDualCLIPLoaderGGUF)
