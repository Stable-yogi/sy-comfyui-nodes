"""CLIP Loader SY: loads one text encoder file, with a choice of model family."""
try:
    from ._sy_common import category, register
    from ._sy_loaders import CLIP_TYPES, CLIP_DEVICES, check_choice, listed_path, embedding_dirs
    from ._sy_model_files import list_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_loaders import CLIP_TYPES, CLIP_DEVICES, check_choice, listed_path, embedding_dirs
    from _sy_model_files import list_names


class SYCLIPLoader:
    DESCRIPTION = "Loads a single text encoder (CLIP) file. Pick the model family it belongs to."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("CLIP",)
    RETURN_NAMES = ("clip",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip_name": (list_names("text_encoders"), {"tooltip": "The text encoder file to load."}),
                "type": (CLIP_TYPES, {"default": "stable_diffusion", "tooltip": "The model family this text encoder is used with."}),
                "device": (CLIP_DEVICES, {"default": "default", "tooltip": "default uses the GPU as usual. cpu keeps the encoder on the CPU."}),
            }
        }

    def run(self, clip_name, type, device):
        check_choice(type, CLIP_TYPES, "type")
        check_choice(device, CLIP_DEVICES, "device")
        path = listed_path("text_encoders", clip_name)
        import torch
        import comfy.sd
        clip_type = getattr(comfy.sd.CLIPType, type.upper(), None)
        if clip_type is None:
            raise ValueError("this ComfyUI does not know the clip type %r. Pick another type" % type)
        options = {}
        if device == "cpu":
            options["load_device"] = options["offload_device"] = torch.device("cpu")
        clip = comfy.sd.load_clip(ckpt_paths=[path], embedding_directory=embedding_dirs(), clip_type=clip_type, model_options=options)
        return (clip,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "CLIPLoader", SYCLIPLoader)
NODE_DISPLAY_NAME_MAPPINGS["SYCLIPLoader"] = "CLIP Loader SY"
