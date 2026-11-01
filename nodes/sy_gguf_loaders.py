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
    from ._sy_a1_files import pick_with_filter, check_size, file_facts, precision_notes, text_encoder_warning
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import find_file
    import _sy_gguf_names as N
    from _sy_a1_files import pick_with_filter, check_size, file_facts, precision_notes, text_encoder_warning


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


_ENCODER_PARTS = ("t5xxl", "umt5", "clip_l", "clip_g", "text_encoder", "gemma", "mistral", "mmproj")


def unet_warnings(name):
    """Pure function. Plain warnings for a file picked in the diffusion model loader."""
    low = str(name).replace("\\", "/").split("/")[-1].lower()
    out = []
    if any(p in low for p in _ENCODER_PARTS) or "t5" in low.replace("-", "_").replace(".", "_").split("_"):
        out.append("The file name looks like a text encoder, not a diffusion model. Use CLIPLoaderGGUF SY for it.")
    return out


def info_for(names_sizes, extra_lines=(), warnings=()):
    """Pure function. names_sizes = [(name, bytes)]. Facts, notes about the file name, then warnings. One line each."""
    lines = []
    for name, size in names_sizes:
        lines.append(file_facts(name, size))
    for name, _ in names_sizes:
        for note in precision_notes(name):
            if note not in lines:
                lines.append(note)
    lines += [x for x in extra_lines if x]
    lines += ["Warning: " + w for w in warnings if w]
    return "\n".join(lines)


def _size_of(path, name):
    import os
    return check_size(name, os.path.getsize(path))


class SYUnetLoaderGGUF:
    DESCRIPTION = ("Loads a GGUF diffusion model (unet). Smaller than the full file and LoRA files still work on it. "
                   "Adds a name_filter box (type part of a name instead of scrolling), a plain info text (size and what the "
                   "Q4/Q8 part of the name means), a warning for a text encoder picked by mistake, and a plain message for an "
                   "empty file. Needs the gguf Python package (the node tells you how to add it).")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "STRING")
    RETURN_NAMES = ("model", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "unet_name": (_gguf_names(N.UNET_KEY), {"tooltip": "The .gguf diffusion model file to load."}),
            },
            "optional": {
                "name_filter": ("STRING", {"default": "", "tooltip": "Optional. Words like 'flux Q4': loads the first matching .gguf and ignores the list."}),
            },
        }

    def run(self, unet_name, name_filter=""):
        chosen, note = pick_with_filter(_gguf_names(N.UNET_KEY), unet_name, name_filter, "GGUF model")
        N.check_unet_name(chosen)
        _ensure_folders()
        path = find_file(N.UNET_KEY, chosen)
        size = _size_of(path, chosen)
        rt = _runtime()
        model = rt.load_unet(path)
        return (model, info_for([(chosen, size)], [note], unet_warnings(chosen)))


class SYCLIPLoaderGGUF:
    DESCRIPTION = ("Loads one text encoder (CLIP) file. It can be a .gguf file or a normal one. Pick the model family. "
                   "Adds a name_filter box, a plain info text, and a warning when the file name and the family do not fit. "
                   "A .gguf file needs the gguf Python package (the node tells you how to add it).")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("CLIP", "STRING")
    RETURN_NAMES = ("clip", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip_name": (_clip_names(), {"tooltip": "The text encoder file to load (.gguf or normal)."}),
                "type": (_clip_types(False), {"default": "stable_diffusion", "tooltip": "The model family this text encoder is used with."}),
            },
            "optional": {
                "name_filter": ("STRING", {"default": "", "tooltip": "Optional. Words like 'umt5 Q8': loads the first matching file and ignores the list."}),
            },
        }

    def run(self, clip_name, type="stable_diffusion", name_filter=""):
        N.check_clip_type(type, _clip_types(False))
        chosen, note = pick_with_filter(_clip_names(), clip_name, name_filter, "text encoder")
        path = _clip_path(chosen)
        size = _size_of(path, chosen)
        rt = _runtime()
        clip = rt.load_clip([path], type)
        return (clip, info_for([(chosen, size)], ["Family: %s" % type, note], [text_encoder_warning(chosen, type)]))


class SYDualCLIPLoaderGGUF:
    DESCRIPTION = ("Loads two text encoder files together. Each can be a .gguf file or a normal one. Pick the model family. "
                   "Adds two name_filter boxes, a plain info text, and a warning when both slots hold the same file or a "
                   "file name does not fit the family. A .gguf file needs the gguf Python package (the node tells you how to add it).")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("CLIP", "STRING")
    RETURN_NAMES = ("clip", "info")

    @classmethod
    def INPUT_TYPES(cls):
        names = _clip_names()
        return {
            "required": {
                "clip_name1": (names, {"tooltip": "The first text encoder file (.gguf or normal)."}),
                "clip_name2": (names, {"tooltip": "The second text encoder file (.gguf or normal)."}),
                "type": (_clip_types(True), {"default": "stable_diffusion", "tooltip": "The model family these two encoders are used with."}),
            },
            "optional": {
                "name_filter1": ("STRING", {"default": "", "tooltip": "Optional. Words for the first file, like 'clip_l'. Ignores the first list."}),
                "name_filter2": ("STRING", {"default": "", "tooltip": "Optional. Words for the second file, like 't5xxl Q8'. Ignores the second list."}),
            },
        }

    def run(self, clip_name1, clip_name2, type="stable_diffusion", name_filter1="", name_filter2=""):
        N.check_clip_type(type, _clip_types(True))
        listed = _clip_names()
        first, note1 = pick_with_filter(listed, clip_name1, name_filter1, "text encoder", "name_filter1")
        second, note2 = pick_with_filter(listed, clip_name2, name_filter2, "text encoder", "name_filter2")
        paths = [_clip_path(first), _clip_path(second)]
        sizes = [_size_of(paths[0], first), _size_of(paths[1], second)]
        rt = _runtime()
        clip = rt.load_clip(paths, type)
        warns = [text_encoder_warning(first, type), text_encoder_warning(second, type)]
        if first == second:
            warns.append("Both slots hold the same file (%s). Two different text encoders are expected." % first)
        return (clip, info_for(list(zip([first, second], sizes)), ["Family: %s" % type, note1, note2], warns))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "UnetLoaderGGUF", SYUnetLoaderGGUF)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CLIPLoaderGGUF", SYCLIPLoaderGGUF)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DualCLIPLoaderGGUF", SYDualCLIPLoaderGGUF)
