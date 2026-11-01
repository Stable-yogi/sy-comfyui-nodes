"""CLIP Loader SY: loads one text encoder file, with a choice of model family, a name filter and plain warnings."""
try:
    from ._sy_common import category, register
    from ._sy_loaders import CLIP_TYPES, CLIP_DEVICES, clip_types, check_choice, listed_path, embedding_dirs
    from ._sy_model_files import list_names
    from ._sy_a1_files import pick_with_filter, check_size, file_facts, precision_notes, text_encoder_warning
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_loaders import CLIP_TYPES, CLIP_DEVICES, clip_types, check_choice, listed_path, embedding_dirs
    from _sy_model_files import list_names
    from _sy_a1_files import pick_with_filter, check_size, file_facts, precision_notes, text_encoder_warning


def build_info(name, size, clip_type, device, filter_note=""):
    """Pure function. Info text: facts, family and device, notes, and a warning when the file and the family do not fit."""
    lines = [file_facts(name, size), "Family: %s, device: %s" % (clip_type, device)]
    if filter_note:
        lines.append(filter_note)
    lines += precision_notes(name)
    warn = text_encoder_warning(name, clip_type)
    if warn:
        lines.append("Warning: " + warn)
    return "\n".join(lines)


class SYCLIPLoader:
    DESCRIPTION = ("Loads a single text encoder (CLIP) file. Adds over the plain loader: a name_filter box to find the file "
                   "without scrolling, a plain info text (size, format, fp8 explained), a warning when the file name and the "
                   "chosen family do not fit (for example a umt5 file with a non-Wan family), and a plain message for an empty file.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("CLIP", "STRING")
    RETURN_NAMES = ("clip", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip_name": (list_names("text_encoders"), {"tooltip": "The text encoder file to load."}),
                "type": (clip_types(), {"default": "stable_diffusion", "tooltip": "The model family this text encoder is used with."}),
                "device": (CLIP_DEVICES, {"default": "default", "tooltip": "default uses the GPU as usual. cpu keeps the encoder on the CPU."}),
            },
            "optional": {
                "name_filter": ("STRING", {"default": "", "tooltip": "Optional. Words like 'umt5 fp8': loads the first matching file and ignores the list."}),
            },
        }

    def run(self, clip_name, type, device, name_filter=""):
        check_choice(type, clip_types(), "type")
        check_choice(device, CLIP_DEVICES, "device")
        chosen, note = pick_with_filter(list_names("text_encoders"), clip_name, name_filter, "text encoder")
        path = listed_path("text_encoders", chosen)
        import os
        import torch
        import comfy.sd
        size = check_size(chosen, os.path.getsize(path))
        clip_type = getattr(comfy.sd.CLIPType, type.upper(), None)
        if clip_type is None:
            raise ValueError("this ComfyUI does not know the clip type %r. Pick another type" % type)
        options = {}
        if device == "cpu":
            options["load_device"] = options["offload_device"] = torch.device("cpu")
        try:
            clip = comfy.sd.load_clip(ckpt_paths=[path], embedding_directory=embedding_dirs(), clip_type=clip_type, model_options=options)
        except (RuntimeError, KeyError, ValueError, AttributeError) as e:
            raise ValueError("could not load %s as a %s text encoder. Check that the file and the type belong together (%s)" % (chosen, type, str(e)[:80]))
        if clip is None:
            raise ValueError("%s is not a text encoder ComfyUI can read as type %s. Pick the matching type or file" % (chosen, type))
        return (clip, build_info(chosen, size, type, device, note))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CLIPLoader", SYCLIPLoader)
NODE_DISPLAY_NAME_MAPPINGS["SYCLIPLoader"] = "CLIP Loader SY"
