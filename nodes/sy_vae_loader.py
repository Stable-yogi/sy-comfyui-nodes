"""VAE Loader SY: loads one VAE file from the vae folder."""
try:
    from ._sy_common import category, register
    from ._sy_loaders import listed_path
    from ._sy_model_files import list_names
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_loaders import listed_path
    from _sy_model_files import list_names


class SYVAELoader:
    DESCRIPTION = "Loads a single VAE file from your vae folder."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("VAE",)
    RETURN_NAMES = ("vae",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vae_name": (list_names("vae"), {"tooltip": "The VAE file to load from the vae folder."}),
            }
        }

    def run(self, vae_name):
        path = listed_path("vae", vae_name)
        import comfy.sd
        import comfy.utils
        sd, metadata = comfy.utils.load_torch_file(path, return_metadata=True)
        vae = comfy.sd.VAE(sd=sd, metadata=metadata)
        vae.throw_exception_if_invalid()
        return (vae,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "VAELoader", SYVAELoader)
NODE_DISPLAY_NAME_MAPPINGS["SYVAELoader"] = "VAE Loader SY"
