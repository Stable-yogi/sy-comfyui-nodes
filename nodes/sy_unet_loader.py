"""Unet Loader SY: loads a diffusion model file, with a choice of weight type."""
try:
    from ._sy_common import category, register
    from ._sy_loaders import UNET_DTYPES, unet_options, listed_path
    from ._sy_model_files import list_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_loaders import UNET_DTYPES, unet_options, listed_path
    from _sy_model_files import list_names


class SYUnetLoader:
    DESCRIPTION = "Loads a diffusion model (unet) file. The weight type can store it smaller in fp8 to save memory."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("model",)

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
        path = listed_path("diffusion_models", unet_name)
        import torch
        import comfy.sd
        model_options = {}
        if opts["dtype"]:
            model_options["dtype"] = getattr(torch, opts["dtype"])
        if opts["fp8_fast"]:
            model_options["fp8_optimizations"] = True
        return (comfy.sd.load_diffusion_model(path, model_options=model_options),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "UnetLoader", SYUnetLoader)
NODE_DISPLAY_NAME_MAPPINGS["SYUnetLoader"] = "Unet Loader SY"
