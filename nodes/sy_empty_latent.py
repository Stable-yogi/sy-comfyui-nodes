"""Empty Latent SY: a blank latent of the right shape for the model family."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

# latent type -> channel count. Both use 8x smaller height and width than the picture.
LATENT_TYPES = {
    "standard 4ch /8": 4,
    "flux 16ch /8": 16,
}
DOWNSCALE = 8
MAX_SIDE = 16384
MAX_BATCH = 4096


def latent_shape(width, height, batch, latent_type):
    """Pure function. Returns (batch, channels, height//8, width//8), like the stock empty latent."""
    if latent_type not in LATENT_TYPES:
        raise ValueError("unknown latent_type %r, pick one of: %s" % (latent_type, ", ".join(LATENT_TYPES)))
    width, height, batch = int(width), int(height), int(batch)
    if width < DOWNSCALE or height < DOWNSCALE:
        raise ValueError("width and height must be at least %d, got %dx%d" % (DOWNSCALE, width, height))
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("width and height must be at most %d, got %dx%d" % (MAX_SIDE, width, height))
    if batch < 1 or batch > MAX_BATCH:
        raise ValueError("batch must be between 1 and %d, got %d" % (MAX_BATCH, batch))
    return (batch, LATENT_TYPES[latent_type], height // DOWNSCALE, width // DOWNSCALE)


class SYEmptyLatent:
    DESCRIPTION = ("Makes a blank latent to start a render from. 'standard 4ch /8' has 4 channels "
                   "(SD 1.5, SDXL). 'flux 16ch /8' has 16 channels (Flux, SD3 style). Both are 8 times smaller than the picture.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 8, "max": MAX_SIDE, "step": 8, "tooltip": "Picture width in pixels."}),
                "height": ("INT", {"default": 1024, "min": 8, "max": MAX_SIDE, "step": 8, "tooltip": "Picture height in pixels."}),
                "batch": ("INT", {"default": 1, "min": 1, "max": MAX_BATCH, "tooltip": "How many blank latents to make at once."}),
                "latent_type": (list(LATENT_TYPES), {"default": "standard 4ch /8", "tooltip": "4 channels for SD 1.5 and SDXL. 16 channels for Flux style models."}),
            }
        }

    def run(self, width, height, batch, latent_type):
        import torch
        shape = latent_shape(width, height, batch, latent_type)
        try:
            import comfy.model_management as mm
            device = mm.intermediate_device()
        except Exception:
            device = "cpu"
        return ({"samples": torch.zeros(list(shape), device=device)},)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EmptyLatent", SYEmptyLatent)
NODE_DISPLAY_NAME_MAPPINGS["SYEmptyLatent"] = "Empty Latent SY"
